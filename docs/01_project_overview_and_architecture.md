# Rice Yield Prediction — Project Overview & Architecture
### Introduction to Machine Learning — Final Project

---

## 1. Project Identity

- **Course context:** Intro to ML final project, three-member team, supervised learning only.
- **Origin note:** This project is a deliberately simplified spin-off of a broader rice-fertilizer research concept the team explored earlier. Individual N/P/K interaction modeling, genotype-by-environment variety matching, and real-time climate/IoT monitoring were all scoped out to fit an intro-course, single-semester, no-deep-learning constraint. What remains is the most machine-learning-friendly, most feasible slice of that original idea.
- **Problem type:** Supervised regression.

## 2. Problem Statement

- **Practical problem:** Rice yield across Philippine provinces varies with combined fertilizer input, climate conditions, and soil chemistry, but there is no simple, localized tool that estimates expected yield from these combined factors at a glance.
- **Prediction target:** `yield_kg_ha` — average palay yield per hectare (continuous).
- **Intended users / context:** Illustrative decision-support use case — e.g., an agricultural extension worker or student estimating expected yield given fertilizer and climate conditions. Not a production/commercial tool.
- **Scope:** Historical, province-level, Philippines-only data.
- **Success criteria:** Four models trained under fair, identical conditions (one reported baseline + three formally compared algorithms), evaluated with RMSE/MAE/R², a justified final model selection, and a working deployed demo.

## 3. Why Machine Learning

Yield response to combined fertilizer application, rainfall, temperature, and soil pH is nonlinear and involves interacting effects (e.g., fertilizer's impact on yield depends on how much rain fell that season). A single fixed formula can't easily capture this; a learned model can.

## 4. Data Sources (Architecture Layer 1)

| Source | What it provides | Granularity |
|---|---|---|
| **PalayStat / PSA** | Palay production, area harvested, yield, input-use & production costs, nutrient management tables | Province × Year (or × Quarter) |
| **Ricelytics** | Builds on PalayStat; adds fertilizer/pesticide price data (via the Fertilizer and Pesticide Authority) and regional aggregates | Province/Region × Year |
| **NASA POWER** | Climate layer: rainfall, temperature, solar radiation, humidity | Queried by province centroid coordinates + date range |
| **ISRIC SoilGrids** | Soil layer: modeled soil pH | Queried by province centroid coordinates |

**Merge key across all sources:** `province + year` (add `season` if quarterly PSA tables are used instead of annual ones).

## 5. Canonical Feature Schema — Single Source of Truth

All three members must use these exact column names going forward. Any deviation must be updated here first.

| Column | Type | Source | Notes |
|---|---|---|---|
| `province` | categorical | PalayStat/PSA | Watch for PSGC province-grouping changes (e.g., Negros Island Region) across years |
| `region` | categorical | Ricelytics | Coarser fallback grouping if a province has too few usable years |
| `year` | integer | PalayStat/PSA | |
| `season` | categorical (wet/dry) | PalayStat/PSA | Only if using quarterly tables |
| `area_harvested_ha` | float | PalayStat/PSA | |
| `fertilizer_total_kg_ha` | float | PalayStat nutrient management table | Primary fertilizer feature |
| `fertilizer_cost_php_ha` | float | PalayStat cost/returns or Ricelytics/FPA | Fallback/complementary if quantity unavailable |
| `rainfall_mm` | float | NASA POWER | Aggregated to cropping season, not plain calendar year, if feasible |
| `avg_temp_c` | float | NASA POWER | |
| `solar_radiation` | float | NASA POWER | Include if consistently available |
| `humidity_pct` | float | NASA POWER | |
| `soil_ph` | float | ISRIC SoilGrids | Document clearly as a modeled/predicted value, not a direct farm measurement |
| `yield_kg_ha` | float | PalayStat/PSA | **Target variable** |

## 6. Pipeline Architecture

```
Stage 1: Data Acquisition & Merge
         (PalayStat + Ricelytics + NASA POWER + SoilGrids → merged panel dataset)
              ↓  [Contract 1]
Stage 2: Exploratory Data Analysis
         (quality checks, distributions, correlations, findings)
              ↓
Stage 3: Feature Engineering & Preprocessing
         (encoding, scaling, train/test split — fit on train only)
              ↓
Stage 4: Model Training (4 models)
         (Linear Regression [baseline] + Ridge, Random Forest, Gradient Boosting [required 3])
              ↓  [Contract 2]
Stage 5: Evaluation & Selection
         (cross-validated comparison, single test-set confirmation, justification)
              ↓  [Contract 3]
Stage 6: Deployment
         (Streamlit app using the final serialized preprocessing + model pipeline)
```

Stages 2–3 and 4 are grouped under Member 1 and Member 2 respectively in the task delegation doc; Stage 5–6 under Member 3. See `03_task_delegation.md` and `02_roadmap_and_contracts.md` for the handoff details.

## 7. Model Roster

Per the course rubric: *"Select exactly three distinct algorithms... A simple baseline may be reported, but it does not replace any of the three required models."*

- **Reported baseline (not one of the three required):** Linear Regression — plain, unregularized, for comparison/reference only.
- **The three formally required, fairly-compared algorithms:**
  1. **Ridge Regression** — regularized linear model; handles multicollinearity between fertilizer, rainfall, and area features better than plain OLS.
  2. **Random Forest Regressor** — bagging ensemble; captures nonlinearity and interactions; yields feature importances.
  3. **Gradient Boosting Regressor** — boosting ensemble; typically strongest raw accuracy; paired against Random Forest for a genuine bagging-vs-boosting comparison.

Final model selection (Stage 5) is made **among the three required models only**. The Linear Regression baseline is used purely as a reference point in the EDA/evaluation narrative (e.g., "our selected model improves RMSE by X% over the naive linear baseline").

## 8. Tech Stack

Python, pandas, numpy, scikit-learn, matplotlib/seaborn, Streamlit, joblib (for serializing the preprocessing pipeline and trained models).

## 9. Constraints Recap (from the course rubric)

- Exactly three distinct required regression algorithms, plus an optional reported baseline.
- No neural networks, deep learning, or AutoML.
- Must be deployed as a simple working application (Streamlit).
- EDA must include: dimensions/types/summary stats, missing values/duplicates/inconsistent entries with actions taken, univariate distributions, target relationships/correlation, outlier investigation, ≥5 meaningful visualizations, and a written findings summary tied to modeling decisions.
- Preprocessing (scaling, encoding) must be fit on training data only, to avoid leakage.

## 10. Non-Goals (explicitly out of scope for this version)

- Individual N/P/K interaction modeling (reserved for the original, larger research concept).
- Genotype-by-environment / variety-region suitability matching.
- Real-time climate forecasting or IoT sensor integration.
- Any deep learning, neural network, or AutoML approach.
