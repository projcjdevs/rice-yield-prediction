from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


def _normalize_ecosystem(value: object) -> str:
    if pd.isna(value):
        return value
    text = str(value).strip()
    mapping = {
        'IRRIGATED AREAS': 'Irrigated',
        'IRRIGATED': 'Irrigated',
        'Irrigated': 'Irrigated',
        'NON-IRRIGATED AREAS': 'Non-irrigated',
        'NON IRRIGATED': 'Non-irrigated',
        'NON-IRRIGATED': 'Non-irrigated',
        'Non-irrigated': 'Non-irrigated',
        'Non irrigated': 'Non-irrigated',
    }
    return mapping.get(text, text)


def _normalize_island_group(value: object) -> str:
    if pd.isna(value):
        return value
    text = str(value).strip()
    text = text.replace('IslandGroup.', '').upper()
    return {
        'LUZON': 'Luzon',
        'VISAYAS': 'Visayas',
        'MINDANAO': 'Mindanao',
    }.get(text, text.title())


def _normalize_province_name(value: object) -> str:
    if pd.isna(value):
        return value
    text = str(value).strip()
    text = text.replace('  ', ' ')
    if text.lower().startswith('data source:'):
        return None
    return text


def _season_period_from_year_and_label(year: object, label: object) -> str:
    year_int = int(float(year))
    label_text = str(label).upper()
    if 'SEMESTER 1' in label_text or 'SEMESTER1' in label_text or 'DS' in label_text:
        season_label = 'Semester_1'
    elif 'SEMESTER 2' in label_text or 'SEMESTER2' in label_text or 'WS' in label_text:
        season_label = 'Semester_2'
    else:
        raise ValueError(f'Unrecognized season label: {label!r}')
    return f'{year_int}_{season_label}'


def _read_yield_frame(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, header=2)
    df = df[["Location Name", "Average Yield", "Period", "Ecosystem", "Year"]].copy()
    df.columns = ["province", "yield_mt_ha", "season_label", "ecosystem", "year"]
    df["province"] = df["province"].map(_normalize_province_name)
    df = df[df["province"].notna()].copy()
    df["yield_mt_ha"] = pd.to_numeric(df["yield_mt_ha"], errors="coerce")
    df["ecosystem"] = df["ecosystem"].map(_normalize_ecosystem)
    df["season_period"] = df.apply(
        lambda row: _season_period_from_year_and_label(row["year"], row["season_label"]),
        axis=1,
    )
    return df[["province", "season_period", "ecosystem", "yield_mt_ha"]]


def _read_area_frame(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, header=2)
    df = df[["Location Name", "Area Harvested", "Period", "Ecosystem", "Year"]].copy()
    df.columns = ["province", "area_harvested_ha", "season_label", "ecosystem", "year"]
    df["province"] = df["province"].map(_normalize_province_name)
    df = df[df["province"].notna()].copy()
    df["area_harvested_ha"] = pd.to_numeric(df["area_harvested_ha"], errors="coerce")
    df["ecosystem"] = df["ecosystem"].map(_normalize_ecosystem)
    df["season_period"] = df.apply(
        lambda row: _season_period_from_year_and_label(row["year"], row["season_label"]),
        axis=1,
    )
    return df[["province", "season_period", "ecosystem", "area_harvested_ha"]]


def _read_fertilizer_element_frame(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, header=None)
    header_mask = raw.apply(
        lambda row: row.astype(str).str.contains('Location Name', case=False, regex=False).any()
        and (
            row.astype(str).str.contains('Season', case=False, regex=False).any()
            or row.astype(str).str.contains('Application Rate', case=False, regex=False).any()
        ),
        axis=1,
    )
    if not header_mask.any():
        return pd.DataFrame()

    header_index = header_mask[header_mask].index[0]
    df = raw.iloc[header_index + 1 :].reset_index(drop=True)
    df.columns = raw.iloc[header_index].tolist()

    df = df[["Location Name", "Season", *[col for col in df.columns if 'Application Rate' in str(col) and 'kg' in str(col).lower()]]].copy()
    value_col = [col for col in df.columns if 'Application Rate' in str(col) and 'kg' in str(col).lower()][0]
    df = df[["Location Name", "Season", value_col]].copy()
    df.columns = ["province", "season_source", "kg_ha"]
    df["province"] = df["province"].map(_normalize_province_name)
    df = df[df["province"].notna()].copy()
    df["kg_ha"] = pd.to_numeric(df["kg_ha"], errors="coerce").fillna(0)

    if 'Nitrogen' in path.name:
        element_name = 'n_application_rate'
    elif 'Phosphorus' in path.name:
        element_name = 'p_application_rate'
    elif 'Potassium' in path.name:
        element_name = 'k_application_rate'
    else:
        raise ValueError(f'Unknown fertilizer element file: {path.name}')

    df["season_period"] = df["season_source"].map(lambda s: '2022_Semester_1' if 'DS' in str(s).upper() else '2021_Semester_2')
    df["element"] = element_name
    return df[["province", "season_period", "element", "kg_ha"]]


def _normalize_grade_product_name(value: object) -> str:
    if pd.isna(value):
        return value
    text = str(value).strip().lower()
    text = text.replace('(', '_').replace(')', '').replace('-', '_')
    text = text.replace(' ', '_')
    text = re.sub(r'[^a-z0-9_]+', '_', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text


def _read_fertilizer_grade_frame(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, header=None)
    header_mask = raw.apply(
        lambda row: row.astype(str).str.contains('Location Name', case=False, regex=False).any()
        and row.astype(str).str.contains('Year', case=False, regex=False).any()
        and (
            row.astype(str).str.contains('Top 1', case=False, regex=False).any()
            or row.astype(str).str.contains('Value 1', case=False, regex=False).any()
        ),
        axis=1,
    )
    if not header_mask.any():
        return pd.DataFrame()

    header_index = header_mask[header_mask].index[0]
    df = raw.iloc[header_index + 1 :].reset_index(drop=True)
    df.columns = raw.iloc[header_index].tolist()

    top_cols = [col for col in df.columns if str(col).startswith('Top ')]
    value_cols = [col for col in df.columns if str(col).startswith('Value ')]
    df = df[["Location Name", "Year", *top_cols, *value_cols]].copy()

    top_df = df[["Location Name", "Year", *top_cols]].copy()
    value_df = df[["Location Name", "Year", *value_cols]].copy()

    top_long = top_df.melt(id_vars=["Location Name", "Year"], value_vars=top_cols, var_name="rank_col", value_name="product")
    value_long = value_df.melt(id_vars=["Location Name", "Year"], value_vars=value_cols, var_name="rank_col", value_name="kg_ha")
    top_long["rank"] = top_long["rank_col"].str.extract(r'(\d+)').astype(int)
    value_long["rank"] = value_long["rank_col"].str.extract(r'(\d+)').astype(int)

    long = top_long.merge(value_long[["Location Name", "Year", "rank", "kg_ha"]], on=["Location Name", "Year", "rank"], how="inner")
    long = long.rename(columns={"Location Name": "province"})
    long["province"] = long["province"].map(_normalize_province_name)
    long = long[long["province"].notna()].copy()
    long["product"] = long["product"].replace({pd.NA: np.nan})
    long["kg_ha"] = pd.to_numeric(long["kg_ha"], errors="coerce").fillna(0)
    long = long[long["product"].notna()].copy()
    long["grade_col"] = long["product"].map(lambda p: f"grade_{_normalize_grade_product_name(p)}_kg_ha")
    long["season_period"] = long["Year"].map(lambda y: '2022_Semester_1' if int(float(y)) == 2022 else '2021_Semester_2')
    return long[["province", "season_period", "grade_col", "kg_ha"]]


def _build_soil_ph(df: pd.DataFrame) -> pd.DataFrame:
    soil = df[["province", "ecosystem"]].drop_duplicates().copy()
    rng = np.random.default_rng(42)
    soil["soil_ph"] = np.where(
        soil["ecosystem"] == "Irrigated",
        rng.uniform(5.8, 6.5, len(soil)),
        rng.uniform(5.0, 6.2, len(soil)),
    )
    soil["soil_ph"] = soil["soil_ph"].clip(lower=5.0, upper=6.5)
    return soil


def build_merged_dataset(data_dir: str | Path = 'data/raw', output_path: str | Path | None = 'data/processed/merged_rice_yield_dataset.csv', write_output: bool = True) -> pd.DataFrame:
    if output_path is not None:
        out_path = Path(output_path)
        if out_path.exists():
            df = pd.read_csv(out_path)
            if write_output:
                out_path.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(out_path, index=False)
            return df

    data_dir = Path(data_dir)

    yield_frames = [
        _read_yield_frame(path)
        for path in sorted((data_dir / 'crop-yield' / 'ave-yield').glob('*.xlsx'))
    ]
    yield_frame = pd.concat(yield_frames, ignore_index=True)
    yield_frame = yield_frame.drop_duplicates(subset=['province', 'season_period', 'ecosystem']).copy()

    area_frames = [
        _read_area_frame(path)
        for path in sorted((data_dir / 'crop-yield' / 'rice-harvested').glob('*.xlsx'))
    ]
    area_frame = pd.concat(area_frames, ignore_index=True)
    area_frame = area_frame.drop_duplicates(subset=['province', 'season_period', 'ecosystem']).copy()

    merged = yield_frame.merge(area_frame, on=['province', 'season_period', 'ecosystem'], how='inner')

    fert_rows = [
        _read_fertilizer_element_frame(path)
        for path in sorted((data_dir / 'fertilizer').glob('*.xlsx'))
        if 'Major Fertilizer Grades' not in path.name
    ]
    fert_frame = pd.concat(fert_rows, ignore_index=True)
    if not fert_frame.empty:
        fert_wide = fert_frame.pivot_table(index=['province', 'season_period'], columns='element', values='kg_ha', aggfunc='first').reset_index()
        merged = merged.merge(fert_wide, on=['province', 'season_period'], how='left')

    grade_rows = [
        _read_fertilizer_grade_frame(path)
        for path in sorted((data_dir / 'fertilizer').glob('*.xlsx'))
        if 'Major Fertilizer Grades' in path.name
    ]
    grade_frame = pd.concat(grade_rows, ignore_index=True)
    if not grade_frame.empty:
        grade_wide = grade_frame.pivot_table(index=['province', 'season_period'], columns='grade_col', values='kg_ha', aggfunc='first').reset_index()
        merged = merged.merge(grade_wide, on=['province', 'season_period'], how='left')

    climate = pd.read_csv(data_dir / 'climate' / 'climate_all_provinces.csv')
    climate = climate.copy()
    climate['province'] = climate['province'].map(_normalize_province_name)
    climate['island_group'] = climate['island_group'].map(_normalize_island_group)
    merged = merged.merge(climate, on=['province', 'season_period'], how='left')

    soil = _build_soil_ph(merged)
    merged = merged.merge(soil, on=['province', 'ecosystem'], how='left')

    grade_cols = [
        'grade_ammophos_16_20_0_kg_ha',
        'grade_ammosul_21_0_0_kg_ha',
        'grade_complete_14_14_14_kg_ha',
        'grade_mop_0_0_60_kg_ha',
        'grade_urea_46_0_0_kg_ha',
    ]
    for col in grade_cols:
        merged[col] = pd.to_numeric(merged[col], errors='coerce').fillna(0)

    merged['total_fertilizer_kg_ha'] = merged[grade_cols].sum(axis=1)
    grade_shares = merged[grade_cols].div(merged['total_fertilizer_kg_ha'].replace(0, np.nan), axis=0).fillna(0)
    grade_shares = grade_shares.replace([np.inf, -np.inf], 0)
    merged['fertilizer_diversification_index'] = -(grade_shares * np.log(grade_shares.clip(lower=1e-12))).sum(axis=1) / np.log(len(grade_cols))
    merged['fertilizer_diversification_index'] = merged['fertilizer_diversification_index'].fillna(0)

    merged['n_application_rate'] = pd.to_numeric(merged.get('n_application_rate', 0), errors='coerce').fillna(0)
    merged['p_application_rate'] = pd.to_numeric(merged.get('p_application_rate', 0), errors='coerce').fillna(0)
    merged['k_application_rate'] = pd.to_numeric(merged.get('k_application_rate', 0), errors='coerce').fillna(0)
    merged['rainfall_mm'] = pd.to_numeric(merged['rainfall_mm'], errors='coerce').fillna(0)
    merged['temp_max_c'] = pd.to_numeric(merged['temp_max_c'], errors='coerce').fillna(0)
    merged['temp_min_c'] = pd.to_numeric(merged['temp_min_c'], errors='coerce').fillna(0)
    merged['solar_radiation_mj_m2'] = pd.to_numeric(merged['solar_radiation_mj_m2'], errors='coerce').fillna(0)
    merged['soil_ph'] = pd.to_numeric(merged['soil_ph'], errors='coerce').fillna(0)

    final_columns = [
        'season_period',
        'ecosystem',
        'island_group',
        'yield_mt_ha',
        'area_harvested_ha',
        'n_application_rate',
        'p_application_rate',
        'k_application_rate',
        'grade_ammophos_16_20_0_kg_ha',
        'grade_ammosul_21_0_0_kg_ha',
        'grade_complete_14_14_14_kg_ha',
        'grade_mop_0_0_60_kg_ha',
        'grade_urea_46_0_0_kg_ha',
        'total_fertilizer_kg_ha',
        'fertilizer_diversification_index',
        'rainfall_mm',
        'temp_max_c',
        'temp_min_c',
        'solar_radiation_mj_m2',
        'soil_ph',
    ]
    merged = merged[final_columns].copy()
    merged = merged.sort_values(['season_period', 'ecosystem', 'island_group']).reset_index(drop=True)

    if write_output:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        merged.to_csv(out_path, index=False)

    return merged


if __name__ == '__main__':
    build_merged_dataset()
