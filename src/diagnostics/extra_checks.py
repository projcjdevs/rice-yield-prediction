"""
Post-hoc diagnostics for the rice-yield project (context only; nothing here is used for model selection).

Run from the repository root:
    python src/diagnostics/extra_checks.py            # full run (about 3-5 minutes)
    python src/diagnostics/extra_checks.py --fast     # skips the learning curve
    python src/diagnostics/extra_checks.py --out artifacts/extra_checks_results.json

What it reproduces
  1. Baselines under the same protocol as the models (global mean, ecosystem mean,
     season x ecosystem x island-group lookup) on LOPO validation and on the sealed test set
  2. Province-level paired bootstrap of RMSE differences (Ridge minus lookup)
  3. Ridge feature-group ablations (LOPO, no augmentation)
  4. Mixup seed sensitivity for Ridge (multipliers 2, 3, 5 over several seeds)
  5. Province-level bootstrap CI for the selected configuration
  6. Train vs LOPO error for Ridge / Random Forest / LightGBM (1x)
  7. Dinagat diagnostics (ecosystem gap, fertilizer profile, Ridge attribution)
  8. Learning curve (training on a fraction of the training provinces)

The test set is used ONLY to score fixed baselines and the already-saved final model.
"""
import argparse, json, sys, warnings
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[2] if Path(__file__).resolve().parent.name == "diagnostics" else Path.cwd()
sys.path.insert(0, str(ROOT))
from src.models.utils.augmentation import stratified_mixup  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--fast", action="store_true")
ap.add_argument("--out", default=str(ROOT / "artifacts" / "extra_checks_results.json"))
args = ap.parse_args()

CAT = ["season_period", "ecosystem", "island_group"]
NUM = ["n_application_rate", "p_application_rate", "k_application_rate", "total_fertilizer_kg_ha",
       "fertilizer_diversification_index", "rainfall_mm", "solar_radiation_mj_m2", "soil_ph",
       "temp_mean_c", "temp_range_c"]
LOG = ["area_harvested_ha"]
FERT = ["n_application_rate", "p_application_rate", "k_application_rate", "total_fertilizer_kg_ha",
        "fertilizer_diversification_index"]
CLIM = ["rainfall_mm", "solar_radiation_mj_m2", "temp_mean_c", "temp_range_c"]
KEY = ["ecosystem", "season_period", "island_group"]
COLS14 = CAT + LOG + ["n_application_rate", "p_application_rate", "k_application_rate", "total_fertilizer_kg_ha",
                      "fertilizer_diversification_index", "rainfall_mm", "solar_radiation_mj_m2", "soil_ph",
                      "temp_mean_c", "temp_range_c"]

df = pd.read_csv(ROOT / "data/processed/merged_rice_yield_dataset.csv")
df["temp_mean_c"] = (df.temp_max_c + df.temp_min_c) / 2
df["temp_range_c"] = df.temp_max_c - df.temp_min_c
split = json.load(open(ROOT / "artifacts/split_provinces.json"))
tr = df[df.province.isin(split["train_provinces"])].reset_index(drop=True)
te = df[df.province.isin(split["test_provinces"])].reset_index(drop=True)
assert len(tr) == 229 and len(te) == 58 and not set(tr.province) & set(te.province)
y, prov = tr.yield_mt_ha.to_numpy(), tr.province.to_numpy()
provs = sorted(tr.province.unique())
strata = (tr.season_period + "|" + tr.ecosystem + "|" + tr.island_group).to_numpy()
oof = pd.read_csv(ROOT / "artifacts/oof_predictions.csv")  # same row order as tr
tp = pd.read_csv(ROOT / "artifacts/test_predictions.csv")


def rmse(a, b): return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))
def r2(a, b): a = np.asarray(a); return float(1 - np.sum((a - b) ** 2) / np.sum((a - a.mean()) ** 2))
def dense(X): return X.toarray() if hasattr(X, "toarray") else X


def make_prep(num=NUM, cat=CAT, log=LOG):
    tf = []
    if num: tf.append(("n", StandardScaler(), num))
    if log: tf.append(("l", Pipeline([("f", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
                                      ("s", StandardScaler())]), log))
    tf.append(("c", OneHotEncoder(drop="first", handle_unknown="ignore"), cat))
    return ColumnTransformer(tf)


def lopo_ridge(num=NUM, cat=CAT, log=LOG, mult=1, seed=42):
    o = np.zeros(len(tr))
    for f, p in enumerate(provs):
        t, v = prov != p, prov == p
        pp = make_prep(num, cat, log)
        Xf, Xv = dense(pp.fit_transform(tr[t])), dense(pp.transform(tr[v]))
        Xa, ya, wa = stratified_mixup(Xf, y[t], strata[t], multiplier=mult, random_state=seed + f)
        o[v] = Ridge(alpha=1.0).fit(Xa, ya, sample_weight=wa).predict(Xv)
    return o


def lopo_group_mean(keys):
    o = np.zeros(len(tr))
    for p in provs:
        t, v = prov != p, prov == p
        gm = y[t].mean()
        if not keys:
            o[v] = gm; continue
        g = tr[t].groupby(keys).yield_mt_ha.mean()
        o[v] = [g.get(tuple(r) if len(keys) > 1 else r[0], gm) for r in tr.loc[v, keys].to_numpy()]
    return o


def test_group_mean(keys):
    gm = tr.yield_mt_ha.mean()
    if not keys: return np.full(len(te), gm)
    g = tr.groupby(keys).yield_mt_ha.mean()
    return np.array([g.get(tuple(r) if len(keys) > 1 else r[0], gm) for r in te[keys].to_numpy()])


R = {}
# 1. baselines ---------------------------------------------------------------------------
base = {"global mean": [], "ecosystem mean": ["ecosystem"], "season x ecosystem x island mean": KEY}
R["baselines"] = {}
for name, k in base.items():
    ov, pt = lopo_group_mean(k), test_group_mean(k)
    R["baselines"][name] = {"lopo_rmse": rmse(y, ov), "lopo_r2": r2(y, ov),
                            "test_rmse": rmse(te.yield_mt_ha, pt), "test_r2": r2(te.yield_mt_ha, pt),
                            "test_mae": float(np.mean(np.abs(te.yield_mt_ha - pt)))}
te["lookup"] = test_group_mean(KEY); tr["lookup"] = lopo_group_mean(KEY)
te = te.merge(tp[["province", "ecosystem", "season_period", "predicted"]], on=["province", "ecosystem", "season_period"]).rename(columns={"predicted": "ridge"})
tr["ridge"] = oof["ridge_m3"].to_numpy()
R["selected_ridge"] = {"lopo_rmse": rmse(y, tr.ridge), "lopo_r2": r2(y, tr.ridge),
                       "test_rmse": rmse(te.yield_mt_ha, te.ridge), "test_r2": r2(te.yield_mt_ha, te.ridge),
                       "test_mae": float(np.mean(np.abs(te.yield_mt_ha - te.ridge)))}

# 2. paired province bootstrap -----------------------------------------------------------------
rng = np.random.default_rng(1)
def pboot(d, a, b, B=4000):
    P = d.province.unique(); idx = {p: np.where(d.province.to_numpy() == p)[0] for p in P}; res = []
    yy, aa, bb = d.yield_mt_ha.to_numpy(), d[a].to_numpy(), d[b].to_numpy()
    for _ in range(B):
        ix = np.concatenate([idx[p] for p in rng.choice(P, len(P), replace=True)])
        res.append(rmse(yy[ix], aa[ix]) - rmse(yy[ix], bb[ix]))
    return {"diff": rmse(yy, aa) - rmse(yy, bb), "ci95": [float(x) for x in np.percentile(res, [2.5, 97.5])],
            "p_first_better": float(np.mean(np.array(res) < 0))}
comb = pd.concat([tr[["province", "yield_mt_ha", "ridge", "lookup"]], te[["province", "yield_mt_ha", "ridge", "lookup"]]], ignore_index=True)
R["paired_ridge_minus_lookup"] = {"validation_60": pboot(tr, "ridge", "lookup"), "test_16": pboot(te, "ridge", "lookup"),
                                  "pooled_76": pboot(comb, "ridge", "lookup")}
te["se_r"] = (te.yield_mt_ha - te.ridge) ** 2; te["se_l"] = (te.yield_mt_ha - te.lookup) ** 2
din = te.province == "Dinagat Islands"
R["test_sse"] = {"ridge_total": float(te.se_r.sum()), "lookup_total": float(te.se_l.sum()),
                 "dinagat_ridge": float(te.se_r[din].sum()), "dinagat_lookup": float(te.se_l[din].sum()),
                 "other54_ridge": float(te.se_r[~din].sum()), "other54_lookup": float(te.se_l[~din].sum()),
                 "rmse_excl_dinagat_ridge": rmse(te.yield_mt_ha[~din], te.ridge[~din]),
                 "rmse_excl_dinagat_lookup": rmse(te.yield_mt_ha[~din], te.lookup[~din])}
pp_ = te.groupby("province")[["se_r", "se_l"]].sum()
R["test_provinces_ridge_better"] = int((pp_.se_r < pp_.se_l).sum())

# 3. ablations ---------------------------------------------------------------------------------
abl = {"full (14 features)": (NUM, CAT, LOG), "full minus soil_ph": ([c for c in NUM if c != "soil_ph"], CAT, LOG),
       "minus climate": ([c for c in NUM if c not in CLIM], CAT, LOG),
       "minus fertilizer": ([c for c in NUM if c not in FERT], CAT, LOG),
       "categorical + area only": ([], CAT, LOG), "categorical only": ([], CAT, []), "ecosystem only": ([], ["ecosystem"], [])}
R["ablation_lopo_ridge_noaug"] = {k: {"rmse": rmse(y, (o := lopo_ridge(*v))), "r2": r2(y, o)} for k, v in abl.items()}

# 4. mixup seeds -------------------------------------------------------------------------------
seeds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 42]
R["mixup_seed_sensitivity"] = {"noaug_1x": rmse(y, lopo_ridge(mult=1))}
for m in (2, 3, 5):
    v = [rmse(y, lopo_ridge(mult=m, seed=s)) for s in seeds]
    R["mixup_seed_sensitivity"][f"{m}x"] = {"seeds": seeds, "rmse": v, "mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1)),
                                            "min": float(min(v)), "max": float(max(v))}

# 5. province bootstrap CI of the selected configuration ---------------------------------------------------
P = tr.province.unique(); idx = {p: np.where(prov == p)[0] for p in P}; vals = []
rr = np.random.default_rng(0)
for _ in range(2000):
    ix = np.concatenate([idx[p] for p in rr.choice(P, len(P), replace=True)]); vals.append(rmse(y[ix], tr.ridge.to_numpy()[ix]))
R["selected_ci_province_bootstrap"] = [float(x) for x in np.percentile(vals, [2.5, 97.5])]

# 6. train vs validation error ---------------------------------------------------------------------------
pp1 = make_prep(); Xtr = dense(pp1.fit_transform(tr))
models = {"ridge": (Ridge(alpha=1.0), "ridge_m1"),
          "random_forest": (RandomForestRegressor(n_estimators=500, min_samples_leaf=2, random_state=42, n_jobs=-1), "random_forest_m1")}
try:
    from lightgbm import LGBMRegressor
    models["lightgbm"] = (LGBMRegressor(n_estimators=200, learning_rate=0.05, num_leaves=7, max_depth=3, min_child_samples=25,
                                        colsample_bytree=0.8, reg_alpha=1.0, reg_lambda=5.0, random_state=42, verbose=-1), "lightgbm_m1")
except ImportError:
    print("lightgbm not installed; skipping that row")
R["train_vs_lopo_1x"] = {}
for n, (m, key) in models.items():
    p_tr = m.fit(Xtr, y).predict(Xtr)
    R["train_vs_lopo_1x"][n] = {"train_rmse": rmse(y, p_tr), "train_r2": r2(y, p_tr), "lopo_rmse": rmse(y, oof[key]), "lopo_r2": r2(y, oof[key])}

# 7. Dinagat -----------------------------------------------------------------------------------------------------
w = df.pivot_table(index=["province", "season_period"], columns="ecosystem", values="yield_mt_ha").dropna()
w["gap"] = w["Irrigated"] - w["Non-irrigated"]
R["dinagat"] = {"gap_median_all": float(w.gap.median()), "n_province_seasons": int(len(w)),
                "gaps": {s: float(w.loc[("Dinagat Islands", s), "gap"]) for s in w.loc["Dinagat Islands"].index},
                "gap_rank_smallest": {s: int(w.gap.rank(method="min").loc[("Dinagat Islands", s)]) for s in w.loc["Dinagat Islands"].index}}
u = df.drop_duplicates(["province", "season_period"])
for s in ["2021_Semester_2", "2022_Semester_1"]:
    x = u[u.season_period == s]; r_ = x[x.province == "Dinagat Islands"].iloc[0]
    R["dinagat"][f"fert_{s}"] = {"p_rank_of_76": int((x.p_application_rate > r_.p_application_rate).sum() + 1),
                                 "k_rank_of_76": int((x.k_application_rate > r_.k_application_rate).sum() + 1),
                                 "total_fert": float(r_.total_fertilizer_kg_ha), "dataset_mean_total": float(x.total_fertilizer_kg_ha.mean())}
sav_pipe = joblib.load(ROOT / "models/preprocessing_pipeline.joblib"); sav_rid = joblib.load(ROOT / "models/model_ridge.joblib")
names = json.load(open(ROOT / "artifacts/feature_order.json"))
R["ridge_coefficients"] = {n: float(c) for n, c in zip(names, sav_rid.coef_)}
R["ridge_coefficients"]["intercept"] = float(sav_rid.intercept_)
R["saved_ridge_test_rmse"] = rmse(te.yield_mt_ha, sav_rid.predict(dense(sav_pipe.transform(te[COLS14]))))

# 8. learning curve ---------------------------------------------------------------------------------
if not args.fast:
    def lc(model_fn, fracs=(0.25, 0.5, 0.75, 1.0), reps=2):
        out = {}
        for fr in fracs:
            vals = []
            for rep in range(reps):
                g = np.random.default_rng(100 + rep); o = np.zeros(len(tr))
                for p in provs:
                    others = [q for q in provs if q != p]
                    keep = g.choice(others, size=max(5, int(round(fr * len(others)))), replace=False)
                    t, v = np.isin(prov, keep), prov == p
                    pp2 = make_prep(); o[v] = model_fn().fit(dense(pp2.fit_transform(tr[t])), y[t]).predict(dense(pp2.transform(tr[v])))
                vals.append(rmse(y, o))
            out[str(fr)] = float(np.mean(vals))
        return out
    R["learning_curve_lopo_rmse"] = {"ridge": lc(lambda: Ridge(alpha=1.0)),
                                     "random_forest_200": lc(lambda: RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=42, n_jobs=-1), reps=1)}

Path(args.out).parent.mkdir(parents=True, exist_ok=True)
json.dump(R, open(args.out, "w"), indent=2)
print(json.dumps(R, indent=2)); print("\nsaved ->", args.out)