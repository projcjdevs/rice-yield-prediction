# Handoff Note: Member 2 → Member 3 (Evaluation & Deployment)

## 1. TL;DR
- Target: provincial palay yield `yield_mt_ha` (t/ha) from 14 features
  (3 categorical + 11 numeric; see feature list in §3).
- Champion config: **Ridge + stratified mixup 3x**. Pooled leave-one-province-out
  (LOPO) OOF RMSE **0.6669** (95% bootstrap CI 0.608–0.718), R² 0.3865.
- Near-tie: linear baseline 0.6681 @3x. Random Forest has best MAE (0.5385 @3x,
  0.5334 @1x) but worse RMSE tail. LightGBM last on RMSE.
- Your job: ONE-TIME evaluation on the sealed 16-province test set + deployment.
  All numbers above are validation-only context, not final verdicts.

## 2. Artifact map
| Path | Purpose |
|---|---|
| `models/preprocessing_pipeline.joblib` | Fitted ColumnTransformer (fit on all 229 train rows) |
| `models/model_{linear_baseline,ridge,random_forest,lightgbm}.joblib` | Final fitted models (trained on 229 real + 458 mixup-synthetic rows, weights 1.0/0.5) |
| `artifacts/feature_order.json` | Exact 15 post-transform column names/order models expect |
| `artifacts/split_provinces.json` | Train (60) / test (16) province lists; seed 42, GroupShuffleSplit(0.2) |
| `artifacts/train_test_split_seed.txt` | Human-readable split documentation |
| `artifacts/model_metrics.csv` | 28 clean rows: technique {none,mixup,copula} × multiplier × model, pooled OOF + per-fold mean±std |
| `artifacts/oof_predictions.csv` | Every train row's OOF prediction per config (source of truth for metrics) |
| `artifacts/bootstrap_cis.csv` | 95% CIs for top configs |
| `docs/eda_findings.md`, `docs/figures/` | EDA findings + figures |
| `notebooks/{01_eda,split,preprocess,augment,train}.ipynb` | Full reproducible pipeline |
| `src/models/utils/augmentation.py`, `augmentation_copula.py` | Mixup / copula generators |

## 3. Inference recipe
1. Build a raw frame with the 14 feature columns: `season_period, ecosystem,
   island_group, area_harvested_ha, n/p/k_application_rate, total_fertilizer_kg_ha,
   fertilizer_diversification_index, rainfall_mm, solar_radiation_mj_m2, soil_ph`
   PLUS recreate row-wise: `temp_mean_c=(temp_max_c+temp_min_c)/2`,
   `temp_range_c=temp_max_c-temp_min_c` (row-wise math, safe anytime).
2. `X = pipeline.transform(df[those 14 cols])` → shape (n, 15); order matches
   `feature_order.json`.
3. `y_hat = model.predict(X)`. No weights, no augmentation at inference.
   **sdv is NOT needed at inference** (copula was a training-time experiment only).

## 4. Rules for the final test evaluation
- Test = 58 rows / 16 provinces listed in `split_provinces.json`; real data only,
  never augmented.
- Evaluate exactly ONCE; report RMSE/MAE/R² (RMSE was the pre-registered primary
  metric). Optionally stratify by ecosystem (irrigated ≈ +0.9 t/ha vs rainfed).
- Do not tune, select, or refit anything using test results.

## 5. Debugging & validation checklist
- Shape check: pipeline output must be (n, 15); compare
  `pipeline.get_feature_names_out()` to `feature_order.json`.
- Silent-failure guard: feeding columns in wrong order produces plausible-looking
  garbage. Always select columns by name, never by position.
- Sanity: predictions far outside [1.2, 6.8] t/ha suggest wrong column order or
  missing temp columns (KeyError on `temp_mean_c` = forgot step 1 recreate).
- Reproduce validation numbers without re-running sweeps:
  RMSE per config = compare `oof_predictions.csv` columns vs train targets
  (train rows = provinces in `split_provinces.json`).
- `model_metrics.csv` rows must all show `n_folds=60`; any 5 means smoke-test
  contamination (happened once; table was rebuilt from OOF predictions).
- Joblib load errors → sklearn/lightgbm version mismatch with the training venv.

## 6. Validation context (so you don't redo it)
- LOPO CV over the 60 train provinces; preprocessing AND augmentation re-fit
  inside every fold (no leakage); pooled OOF = headline metric.
- Mixup ladder {1,2,3,5}: 3x best (cross-model mean RMSE 0.6775 vs 0.6826 none).
- Copula arm (sdv GaussianCopula, 'norm' marginals): generator validated
  (correlations/strata preserved) but no multiplier beat mixup (0.694–0.701).
  Documented negative result.
- All bootstrap CIs overlap; champion chosen by pre-registered point-estimate rule.

## 7. Limitations to cite in discussion
Coarse predictors (province-average fertilizer, season-aggregated climate);
simulated `soil_ph`; CIs overlap across configs; Nueva Ecija (6.77 t/ha) is an
influential high-yield point; tree models degrade under augmentation while
linear models improve.