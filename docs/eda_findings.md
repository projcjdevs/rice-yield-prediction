# EDA Findings & Data Audit

This document summarizes the data quality, feature engineering decisions, and exploratory findings for the Philippine Rice Yield Prediction project.

## 1. Data Provenance and Quality Verification
- **Source:** Merged dataset of 287 rows across 76 provinces, 2 season periods (2021 Semester 2, 2022 Semester 1), and 2 ecosystems (Irrigated, Non-irrigated).
- **Dimensions:** 287 rows × 21 original columns (now 15 after feature engineering).
- **Completeness:** 0 missing cells; 0 duplicate rows; 0 duplicate `province + season + ecosystem` keys.
- **Internal Consistency:** Derived feature `total_fertilizer_kg_ha` was verified to match the sum of its 5 grade components (max absolute diff ≈ 5.7e-14, i.e., floating-point noise).
- **Outliers (1.5 × IQR rule):** Two observations were flagged:
  1. Davao Occidental (Non-irrigated, yield 1.22): Consistent with rainfed conditions and below-average fertilizer.
  2. Nueva Ecija (Irrigated, yield 6.77): Co-occurs with the dataset's maximum fertilizer rate (599.78 kg/ha).
  *Decision:* Both retained as real, internally consistent extremes, not data errors. The high-yield point will be noted as a potential influential observation for linear models.

## 2. Target Variable (`yield_mt_ha`)
- **Distribution:** Mean (3.61) ≈ Median (3.59). Skewness ≈ 0.06.
- **Finding:** The target is highly symmetric.
- **Decision:** No log or power transformation is needed for the target variable.

## 3. Feature Engineering & Selection
- **Temperature:** Raw `temp_max_c` and `temp_min_c` were highly correlated (r = 0.848). 
  - *Decision:* Created `temp_mean_c` and `temp_range_c` (day-night swing) to better reflect crop biology, then dropped the raw bounds to prevent multicollinearity.
- **Fertilizer:** Raw masses of 5 specific fertilizer grades were highly correlated with `total_fertilizer_kg_ha` and elemental rates (N, P, K).
  - *Decision:* Dropped the 5 grade columns to prevent redundancy. Kept N, P, K elemental rates, total mass, and diversification index.
- **Area (`area_harvested_ha`):** Heavily right-skewed (skewness = 3.158). Irrigated farms are on average >2x larger than non-irrigated farms.
  - *Decision:* Retained due to strong correlation with yield (r = 0.437). Will apply a log-transform (`np.log1p`) during preprocessing.

## 4. Final Feature Matrix (14 Predictors + 1 Target)
- **Categorical:** `season_period`, `ecosystem`, `island_group`
- **Numeric:** `area_harvested_ha`, `n_application_rate`, `p_application_rate`, `k_application_rate`, `total_fertilizer_kg_ha`, `fertilizer_diversification_index`, `rainfall_mm`, `solar_radiation_mj_m2`, `soil_ph`, `temp_mean_c`, `temp_range_c`
- **Target:** `yield_mt_ha`

## 5. Methodological Caveats
- `province` is strictly an identifier for grouped cross-validation; it is not a trained feature.
- `soil_ph` is simulated (anchored to 5.0–6.5 ranges) and represents one value per province+ecosystem. Correlations involving it are descriptive, not measured field evidence.
- `area_harvested_ha` is treated as a proxy for farm management/infrastructure scale, not a direct causal driver of per-hectare yield.