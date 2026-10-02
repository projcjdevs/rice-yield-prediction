"""Build and profile the provincial rice-yield sourcing dataset."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
YIELD_DIR = RAW / "crop-yield" / "ave-yield"
AREA_DIR = RAW / "crop-yield" / "rice-harvested"
FERT_DIR = RAW / "fertilizer"
CLIMATE_FILE = RAW / "climate" / "climate_all_provinces.csv"
DOCS = ROOT / "docs"
FIGURES = DOCS / "figures"
OUTPUT = ROOT / "data" / "processed" / "merged_rice_yield_dataset.csv"
SEASONS = {
    "2022_Semester_1": (2022, "Semester 1", "2022 DS"),
    "2021_Semester_2": (2021, "Semester 2", "2021 WS"),
}
PROVINCE_ALIASES = {
    "cotabato": "North Cotabato",
    "samar": "Western Samar",
    "surigao del norte": "Surigao del Norte",
    "surigao del sur": "Surigao del Sur",
}
ECOSYSTEMS = {"irrigated": "Irrigated", "non-irrigated": "Non-irrigated"}
ELEMENTS = {"nitrogen": "n_application_rate", "phosphorus": "p_application_rate", "potassium": "k_application_rate"}
SLOTS = range(1, 6)
NULL_POLICY = (
    "A present fertilizer record with a missing element rate or incomplete named grade rank is excluded, not filled with zero. "
    "A grade absent from the reported top-five list is encoded as zero, meaning unlisted rather than confirmed zero use. "
    "A province absent from a source is not imputed."
)


def text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def canonical_province(value: Any) -> str:
    name = text(value)
    return PROVINCE_ALIASES.get(name.casefold(), name)


def workbook(folder: Path, fragment: str) -> Path:
    matches = [p for p in folder.glob("*.xlsx") if fragment.casefold() in p.name.casefold()]
    if len(matches) != 1:
        raise FileNotFoundError(f"Expected one workbook matching {fragment!r} in {folder}; got {len(matches)}")
    return matches[0]


def sheet(path: Path, required: set[str]) -> pd.DataFrame:
    for header in range(6):
        frame = pd.read_excel(path, header=header)
        frame.columns = [text(c) for c in frame.columns]
        if required.issubset(frame.columns):
            return frame
    raise ValueError(f"Header with {sorted(required)} not found in {path.name}")


def provinces(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.rename(columns={"Location Name": "province"}).copy()
    frame["province"] = frame["province"].map(canonical_province)
    return frame[frame["province"].ne("") & ~frame["province"].str.casefold().str.startswith("data source:")]


def unique(frame: pd.DataFrame, keys: list[str], label: str) -> None:
    dupes = frame.loc[frame.duplicated(keys, keep=False), keys].head(8).to_dict("records")
    if dupes:
        raise ValueError(f"{label} duplicate keys {keys}: {dupes}")


def load_yield_area() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, set[str]]]:
    ys, areas = [], []
    coverage = {"yield": set(), "area": set()}
    for season, (year, period, _) in SEASONS.items():
        for ecosystem, label in ECOSYSTEMS.items():
            eco_file = "Non-irrigated Areas" if ecosystem == "non-irrigated" else "Irrigated Areas"
            y = provinces(sheet(workbook(YIELD_DIR, f"{year} {period} Average Yield of Palay in {eco_file}"), {"Location Name", "Average Yield"}))
            y["yield_mt_ha"] = pd.to_numeric(y["Average Yield"], errors="coerce")
            y["season_period"], y["ecosystem"] = season, label
            ys.append(y[["province", "season_period", "ecosystem", "yield_mt_ha"]])
            coverage["yield"].update(y["province"])
            a = provinces(sheet(workbook(AREA_DIR, f"{year} {period} Rice Area Harvested in {eco_file}"), {"Location Name", "Area Harvested"}))
            a["area_harvested_ha"] = pd.to_numeric(a["Area Harvested"], errors="coerce")
            a["season_period"], a["ecosystem"] = season, label
            areas.append(a[["province", "season_period", "ecosystem", "area_harvested_ha"]])
            coverage["area"].update(a["province"])
    yields, areas = pd.concat(ys, ignore_index=True), pd.concat(areas, ignore_index=True)
    unique(yields, ["province", "season_period", "ecosystem"], "yield")
    unique(areas, ["province", "season_period", "ecosystem"], "area")
    return yields, areas, coverage


def load_elements() -> tuple[pd.DataFrame, set[str], list[dict[str, str]]]:
    parts, coverage, nulls = [], set(), []
    for season, (_, _, fertilizer_season) in SEASONS.items():
        for element, output in ELEMENTS.items():
            path = workbook(FERT_DIR, f"{fertilizer_season} Average Application Rate of {element.title()} Fertilizer")
            first = sheet(path, {"Location Name"})
            value_col = next((c for c in first.columns if c.casefold().startswith("application rate of ")), None)
            if value_col is None:
                raise ValueError(f"No application-rate field found in {path.name}")
            frame = provinces(sheet(path, {"Location Name", value_col}))
            frame["kg_ha"] = pd.to_numeric(frame[value_col], errors="coerce")
            frame["season_period"], frame["element"] = season, element
            coverage.update(frame["province"])
            nulls.extend({"source": path.name, "province": p, "reason": f"missing {output}"} for p in frame.loc[frame["kg_ha"].isna(), "province"])
            parts.append(frame[["province", "season_period", "element", "kg_ha"]])
    long = pd.concat(parts, ignore_index=True)
    unique(long, ["province", "season_period", "element"], "element fertilizer")
    wide = long.pivot(index=["province", "season_period"], columns="element", values="kg_ha").reset_index().rename(columns=ELEMENTS)
    wide.columns.name = None
    return wide, coverage, nulls


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.casefold()).strip("_") or "unknown"


def load_grades() -> tuple[pd.DataFrame, set[str], list[dict[str, str]], list[str]]:
    chunks, coverage, nulls = [], set(), []
    incomplete_keys: set[tuple[str, str]] = set()
    for season, (_, _, fertilizer_season) in SEASONS.items():
        path = workbook(FERT_DIR, f"{fertilizer_season} Major Fertilizer Grades Applied")
        required = {"Location Name"} | {f"{kind} {i}" for kind in ("Top", "Value") for i in SLOTS}
        frame = provinces(sheet(path, required))
        coverage.update(frame["province"])
        records = []
        for _, row in frame.iterrows():
            province, invalid = row["province"], False
            for i in SLOTS:
                product, amount = text(row[f"Top {i}"]), pd.to_numeric(row[f"Value {i}"], errors="coerce")
                if not product and pd.isna(amount):
                    continue
                if not product or pd.isna(amount):
                    invalid = True
                    nulls.append({"source": path.name, "province": province, "reason": f"incomplete top/value rank {i}"})
                    continue
                records.append({"province": province, "season_period": season, "product": product, "kg_ha": float(amount)})
            if invalid:
                incomplete_keys.add((province, season))
        chunks.append(pd.DataFrame(records))
    long = pd.concat(chunks, ignore_index=True)
    long = long[~long.apply(lambda r: (r["province"], r["season_period"]) in incomplete_keys, axis=1)]
    long["grade_column"] = "grade_" + long["product"].map(slug) + "_kg_ha"
    unique(long, ["province", "season_period", "product"], "grade fertilizer")
    wide = long.pivot(index=["province", "season_period"], columns="grade_column", values="kg_ha").reset_index()
    wide.columns.name = None
    grades = sorted(c for c in wide if c.startswith("grade_"))
    wide[grades] = wide[grades].fillna(0)
    total = wide[grades].sum(axis=1)
    share = wide[grades].div(total.replace(0, np.nan), axis=0)
    wide["total_fertilizer_kg_ha"] = total
    wide["fertilizer_diversification_index"] = -(share.where(share.gt(0), 1).apply(np.log) * share).sum(axis=1).fillna(0)
    return wide, coverage, nulls, grades


def load_climate() -> tuple[pd.DataFrame, set[str]]:
    if not CLIMATE_FILE.exists():
        raise FileNotFoundError(f"Missing {CLIMATE_FILE}. Run `python build_dataset.py --fetch-climate` first.")
    data = pd.read_csv(CLIMATE_FILE)
    required = {"province", "island_group", "season_period", "rainfall_mm", "temp_max_c", "temp_min_c", "solar_radiation_mj_m2"}
    if not required.issubset(data.columns):
        raise ValueError(f"Climate file missing: {sorted(required - set(data.columns))}")
    data["province"] = data["province"].map(canonical_province)
    data["island_group"] = data["island_group"].map(text).str.replace(r"^IslandGroup\.", "", regex=True).str.title()
    data = data[data["season_period"].isin(SEASONS)]
    unique(data, ["province", "season_period"], "climate")
    return data, set(data["province"])


def soil_ph(frame: pd.DataFrame) -> pd.DataFrame:
    values = {}
    for province, ecosystem in frame[["province", "ecosystem"]].drop_duplicates().itertuples(index=False, name=None):
        seed = int.from_bytes(hashlib.sha256(f"{province}|{ecosystem}".encode()).digest()[:8], "big")
        rng = np.random.default_rng(seed)
        limits = (5.6, 6.5) if ecosystem == "Irrigated" else (5.0, 6.1)
        values[(province, ecosystem)] = round(float(rng.uniform(*limits)), 2)
    frame["soil_ph"] = [values[(p, e)] for p, e in zip(frame["province"], frame["ecosystem"])]
    return frame


def reconcile(sources: dict[str, set[str]]) -> dict[str, Any]:
    names = sorted(set().union(*sources.values()))
    table = pd.DataFrame({"province": names})
    for source, present in sources.items():
        table[source] = table["province"].isin(present)
    table["absent_from"] = table.apply(lambda r: ", ".join(s for s in sources if not r[s]), axis=1)
    table.to_csv(DOCS / "province_reconciliation.csv", index=False)
    missing = table.loc[table["absent_from"].ne(""), ["province", "absent_from"]].to_dict("records")
    return {"source_counts": {k: len(v) for k, v in sources.items()}, "dropped_provinces": [{**r, "reason": f"absent from: {r['absent_from']}"} for r in missing]}


def data_dictionary(columns: list[str], grade_columns: list[str]) -> None:
    details = {
        "season_period": ("PSA yield period/year matched to the corresponding fertilizer season.", "category"),
        "ecosystem": ("PSA rice ecosystem.", "category"),
        "island_group": ("PSGC island group; used instead of raw province for geographic modeling.", "category"),
        "yield_mt_ha": ("Average palay yield from PSA.", "metric tons/ha"),
        "area_harvested_ha": ("Rice area harvested from PSA; see source definition.", "as reported"),
        "n_application_rate": ("Nitrogen rate. Source says kg; per-hectare interpretation is assumed, not confirmed.", "assumed kg/ha"),
        "p_application_rate": ("Phosphorus rate. Source says kg; per-hectare interpretation is assumed, not confirmed.", "assumed kg/ha"),
        "k_application_rate": ("Potassium rate. Source says kg; per-hectare interpretation is assumed, not confirmed.", "assumed kg/ha"),
        "total_fertilizer_kg_ha": ("Sum of listed top-five fertilizer grades; inherits the unit assumption.", "assumed kg/ha"),
        "fertilizer_diversification_index": ("Shannon entropy of shares among listed top-five grades.", "dimensionless"),
        "rainfall_mm": ("Semester total daily precipitation from Open-Meteo archive.", "mm"),
        "temp_max_c": ("Mean daily maximum temperature over semester.", "deg C"),
        "temp_min_c": ("Mean daily minimum temperature over semester.", "deg C"),
        "solar_radiation_mj_m2": ("Mean daily shortwave radiation over semester.", "MJ/m^2/day"),
        "soil_ph": ("Fixed-seed simulated proxy per province/ecosystem; not measured.", "simulated pH"),
    }
    for col in grade_columns:
        details[col] = (f"Quantity of reported top-five grade {col[6:-6].replace('_', ' ')}; absent means unlisted, not proven zero use.", "assumed kg/ha")
    lines = ["# Data Dictionary", "", "One row represents a province-season-ecosystem observation. `province` is retained for auditability and leave-one-province-out grouping; use `island_group` as the geographic model feature. See `province_reconciliation.csv` and `sourcing_audit.json`.", "", "By-element source headers say `kg` without an explicit per-hectare denominator. Treating those values as `kg/ha` is an assumption based on plausible magnitudes, not a confirmed source unit. `soil_ph` is simulated, reproducible, and not a measurement.", "", "## Columns", "", "| Column | Description / source | Unit or type |", "|---|---|---|"]
    for col in columns:
        description, unit = details.get(col, ("See source audit.", "source-derived"))
        lines.append(f"| `{col}` | {description} | {unit} |")
    (DOCS / "data_dictionary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_eda(frame: pd.DataFrame, audit: dict[str, Any]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    numeric = frame.select_dtypes(include="number")
    correlations = numeric.corr(numeric_only=True)["yield_mt_ha"].drop("yield_mt_ha").sort_values(key=lambda s: s.abs(), ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5)); ax.hist(frame["yield_mt_ha"], bins=18, color="#247a68", edgecolor="white"); ax.set(title="Rice yield distribution", xlabel="Yield (metric tons/ha)", ylabel="Rows"); fig.tight_layout(); fig.savefig(FIGURES / "yield_distribution.png", dpi=150); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 5)); ax.boxplot([frame.loc[frame.ecosystem.eq(e), "yield_mt_ha"] for e in ECOSYSTEMS.values()], tick_labels=list(ECOSYSTEMS.values())); ax.set(title="Yield by ecosystem", ylabel="Yield (metric tons/ha)"); fig.tight_layout(); fig.savefig(FIGURES / "yield_by_ecosystem.png", dpi=150); plt.close(fig)
    corr = numeric.corr(numeric_only=True); fig, ax = plt.subplots(figsize=(10, 8)); image = ax.imshow(corr, cmap="RdYlBu_r", vmin=-1, vmax=1); ax.set_xticks(range(len(corr)), corr.columns, rotation=75, ha="right"); ax.set_yticks(range(len(corr)), corr.columns); ax.set_title("Numeric feature correlation matrix"); fig.colorbar(image, ax=ax); fig.tight_layout(); fig.savefig(FIGURES / "correlation_matrix.png", dpi=150); plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 5));
    for ecosystem, group in frame.groupby("ecosystem"):
        ax.scatter(group["total_fertilizer_kg_ha"], group["yield_mt_ha"], label=ecosystem, alpha=.65)
    ax.set(title="Yield and reported top-five fertilizer total", xlabel="Reported grade total (assumed kg/ha)", ylabel="Yield (metric tons/ha)"); ax.legend(); fig.tight_layout(); fig.savefig(FIGURES / "yield_vs_fertilizer.png", dpi=150); plt.close(fig)
    means = frame.groupby(["season_period", "ecosystem"])["yield_mt_ha"].mean().unstack(); fig, ax = plt.subplots(figsize=(8, 5)); means.plot(kind="bar", ax=ax, color=["#247a68", "#df9f3c"]); ax.set(title="Mean yield by season and ecosystem", ylabel="Yield (metric tons/ha)", xlabel="Season"); ax.tick_params(axis="x", rotation=15); fig.tight_layout(); fig.savefig(FIGURES / "season_ecosystem_yield.png", dpi=150); plt.close(fig)
    q1, q3 = frame["yield_mt_ha"].quantile([.25, .75]); iqr = q3 - q1
    outliers = frame.loc[frame.yield_mt_ha.lt(q1 - 1.5 * iqr) | frame.yield_mt_ha.gt(q3 + 1.5 * iqr), ["season_period", "ecosystem", "yield_mt_ha"]]
    outliers.to_csv(DOCS / "yield_iqr_outliers.csv", index=False)
    corr_text = "\n".join(f"- `{k}`: {v:.3f}" for k, v in correlations.items()) or "- No numeric correlations available."
    stats = frame.describe(include="all").transpose().to_markdown(floatfmt=".3f")
    types = "\n".join(f"- `{c}`: `{t}`" for c, t in frame.dtypes.astype(str).items())
    missing = "\n".join(f"- `{c}`: {int(n)}" for c, n in frame.isna().sum().items())
    coverage = pd.DataFrame(audit["yield_area_coverage"])
    coverage_table = coverage.to_markdown(index=False)
    focus = coverage.loc[
        coverage["season_period"].eq("2022_Semester_1")
        & coverage["ecosystem"].eq("Non-irrigated")
    ].iloc[0]
    missing_area = [
        row["province"]
        for row in audit["yield_without_area_keys"]
        if row["season_period"] == "2022_Semester_1"
        and row["ecosystem"] == "Non-irrigated"
    ]
    join_counts = pd.DataFrame(audit["join_stage_counts"])
    join_counts = (
        join_counts.pivot(
            index=["season_period", "ecosystem"], columns="stage", values="rows"
        )
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    join_counts_table = join_counts.to_markdown(index=False)
    pH_groups = frame.groupby(["province", "ecosystem"])["soil_ph"].nunique()
    inconsistent_pH = int(pH_groups.gt(1).sum())
    pictures = ["yield_distribution.png: inspects target spread and skew.", "yield_by_ecosystem.png: compares irrigated/non-irrigated yield distributions.", "correlation_matrix.png: summarizes pairwise numeric associations.", "yield_vs_fertilizer.png: compares yield with listed grade totals.", "season_ecosystem_yield.png: compares means by season and ecosystem."]
    report = f"""# EDA Findings

## Dataset profile

- Final dimensions: {len(frame)} rows x {len(frame.columns)} columns.
- Duplicate rows: {int(frame.duplicated().sum())}.
- Target nulls: {int(frame.yield_mt_ha.isna().sum())}.

{stats}

## Types and missing values

{types}

Missing values after merge:

{missing}

Null policy: {NULL_POLICY}

## Province coverage and exclusions

Counts by source: `{json.dumps(audit['province_reconciliation']['source_counts'], sort_keys=True)}`. Full province-by-source flags and names absent from sources are in `province_reconciliation.csv` and `sourcing_audit.json`. Incomplete fertilizer rows excluded: `{json.dumps(audit['dropped_rows_by_source'], sort_keys=True)}`.

## Yield/area coverage and pH checks

{coverage_table}

For 2022 Semester 1 Non-irrigated, the source contains {int(focus['yield_source_rows'])} yield rows and {int(focus['area_matches'])} matching harvested-area rows. The unmatched yield record is {', '.join(missing_area) if missing_area else 'none'}. The lower row count is present in the source coverage; the merge did not discard a row with a matching area key. An absent source record is unreported data, not proof of zero rice area. The final soil-pH check found {inconsistent_pH} province/ecosystem groups with differing values across season-years (expected: 0).

Rows remaining through successive source joins:

{join_counts_table}

Later reductions occur at the corresponding inner join when a source key is absent; the stage counts make those exclusions explicit rather than silently attributing them to the yield/area merge.

## Target correlations

{corr_text}

These are descriptive associations, not causal effects. Soil pH is simulated and climate summaries hide within-province variation.

## Outliers

The 1.5 x IQR rule flags {len(outliers)} yield observations. See `yield_iqr_outliers.csv`; verify them against source workbooks before exclusion.

## Visualizations

{chr(10).join('- `figures/' + p + '`' for p in pictures)}

## Notes for Member 2

- Use `island_group` as the geographic model feature and retain `province` for leave-one-province-out grouping and auditability.
- Do not describe `soil_ph` as measured data.
- The fertilizer kg-to-kg/ha conversion is an assumption.
- Grade totals and entropy use only reported top-five quantities; absent grades are encoded as zero/unlisted.
- Only two season-years are included; split validation by province to avoid leakage.
"""
    (DOCS / "eda_findings.md").write_text(report, encoding="utf-8")


def build() -> pd.DataFrame:
    DOCS.mkdir(parents=True, exist_ok=True)
    yields, areas, coverage = load_yield_area()
    elements, ep, element_nulls = load_elements()
    grades, gp, grade_nulls, grade_columns = load_grades()
    climate, cp = load_climate()
    coverage.update({"fertilizer_elements": ep, "fertilizer_grades": gp, "climate": cp})
    province_report = reconcile(coverage)
    area_join = yields.merge(areas[["province", "season_period", "ecosystem"]], on=["province", "season_period", "ecosystem"], how="left", indicator=True)
    yield_area_coverage = (
        area_join.groupby(["season_period", "ecosystem"], as_index=False)
        .agg(
            yield_source_rows=("province", "size"),
            area_matches=("_merge", lambda values: int(values.eq("both").sum())),
            yield_rows_without_area=("_merge", lambda values: int(values.eq("left_only").sum())),
        )
        .to_dict("records")
    )
    yield_without_area_keys = area_join.loc[
        area_join["_merge"].eq("left_only"), ["province", "season_period", "ecosystem"]
    ].to_dict("records")
    merged = yields.merge(areas, on=["province", "season_period", "ecosystem"], how="inner", validate="one_to_one")
    join_stage_counts = []

    def record_join_stage(stage: str, frame: pd.DataFrame) -> None:
        for (season, ecosystem), rows in frame.groupby(["season_period", "ecosystem"]).size().items():
            join_stage_counts.append({"stage": stage, "season_period": season, "ecosystem": ecosystem, "rows": int(rows)})

    record_join_stage("yield+area", merged)
    merged = merged.merge(elements, on=["province", "season_period"], how="inner", validate="many_to_one")
    record_join_stage("+elements", merged)
    merged = merged.merge(grades, on=["province", "season_period"], how="inner", validate="many_to_one")
    record_join_stage("+grades", merged)
    merged = merged.merge(climate, on=["province", "season_period"], how="inner", validate="many_to_one")
    record_join_stage("+climate", merged)
    merged = soil_ph(merged)
    required = ["yield_mt_ha", "area_harvested_ha", *ELEMENTS.values(), *grade_columns, "rainfall_mm", "temp_max_c", "temp_min_c", "solar_radiation_mj_m2"]
    before_drop = len(merged)
    merged = merged.dropna(subset=required).copy()
    missing_required = before_drop - len(merged)
    unique(merged, ["province", "season_period", "ecosystem"], "merged data")
    order = ["season_period", "ecosystem", "province", "island_group", "yield_mt_ha", "area_harvested_ha", *ELEMENTS.values(), *grade_columns, "total_fertilizer_kg_ha", "fertilizer_diversification_index", "rainfall_mm", "temp_max_c", "temp_min_c", "solar_radiation_mj_m2", "soil_ph"]
    merged = merged[order].sort_values(["season_period", "island_group", "province", "ecosystem"]).reset_index(drop=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUTPUT, index=False)
    audit = {
        "row_count": len(merged), "column_count": len(merged.columns),
        "dropped_rows_by_source": {
            "yield_without_area_match": int(area_join["_merge"].eq("left_only").sum()),
            "incomplete_element_records": len(element_nulls),
            "incomplete_grade_records": len(grade_nulls),
            "required_nulls_after_merge": missing_required,
        },
        "yield_area_coverage": yield_area_coverage,
        "yield_without_area_keys": yield_without_area_keys,
        "join_stage_counts": join_stage_counts,
        "element_null_records": element_nulls, "grade_null_records": grade_nulls,
        "province_aliases_applied_to_climate": PROVINCE_ALIASES,
        "province_reconciliation": province_report,
        "dropped_provinces": province_report["dropped_provinces"], "null_policy": NULL_POLICY,
    }
    (DOCS / "sourcing_audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    data_dictionary(list(merged.columns), grade_columns)
    make_eda(merged, audit)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {len(merged)} rows x {len(merged.columns)} columns")
    print(f"Provinces not represented in every source: {json.dumps(province_report['dropped_provinces'], ensure_ascii=False)}")
    print(f"Incomplete fertilizer rows reported: {len(element_nulls) + len(grade_nulls)}")
    return merged


def fetch_climate() -> None:
    try:
        import psgc
        import requests
    except ImportError as exc:
        raise RuntimeError("Install requirements-sourcing.txt before fetching climate.") from exc
    CLIMATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    windows = {"2022_Semester_1": ("2022-01-01", "2022-06-30"), "2021_Semester_2": ("2021-07-01", "2021-12-31")}
    daily_fields = "temperature_2m_max,temperature_2m_min,precipitation_sum,shortwave_radiation_sum"
    rows, failures = [], []
    for province in (p for p in psgc.provinces if not p.is_pseudo):
        coord = province.coordinate
        if coord is None:
            failures.append({"province": province.name, "reason": "no coordinate"})
            continue
        for season, (start, end) in windows.items():
            params = {"latitude": coord.latitude, "longitude": coord.longitude, "start_date": start, "end_date": end, "daily": daily_fields, "timezone": "Asia/Manila", "format": "json"}
            payload = None
            for attempt in range(1, 6):
                try:
                    response = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=60)
                    if response.status_code == 429:
                        time.sleep(int(response.headers.get("Retry-After", 10 * attempt)))
                        continue
                    response.raise_for_status()
                    payload = response.json()
                    if "daily" not in payload:
                        raise ValueError("Response contains no daily data")
                    break
                except (requests.RequestException, ValueError) as exc:
                    if attempt == 5:
                        failures.append({"province": province.name, "reason": f"{season}: {exc}"})
                    else:
                        time.sleep(5 * attempt)
            if payload is None:
                continue
            daily = payload["daily"]
            fields = ["precipitation_sum", "temperature_2m_max", "temperature_2m_min", "shortwave_radiation_sum"]
            if any(not daily.get(k) for k in fields):
                failures.append({"province": province.name, "reason": f"{season}: missing daily values"})
                continue
            rows.append({
                "province": province.name, "island_group": str(province.island_group), "season_period": season,
                "rainfall_mm": sum(daily["precipitation_sum"]),
                "temp_max_c": float(np.mean(daily["temperature_2m_max"])),
                "temp_min_c": float(np.mean(daily["temperature_2m_min"])),
                "solar_radiation_mj_m2": float(np.mean(daily["shortwave_radiation_sum"])),
            })
            time.sleep(1.5)
    pd.DataFrame(rows).to_csv(CLIMATE_FILE, index=False)
    if failures:
        pd.DataFrame(failures).to_csv(CLIMATE_FILE.parent / "climate_failures.csv", index=False)
    print(f"Wrote {CLIMATE_FILE.relative_to(ROOT)}: {len(rows)} rows; failed pairs: {len(failures)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-climate", action="store_true", help="Fetch semester climate aggregates from Open-Meteo.")
    args = parser.parse_args()
    if args.fetch_climate:
        fetch_climate()
    build()


if __name__ == "__main__":
    main()
