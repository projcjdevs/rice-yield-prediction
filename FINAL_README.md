# 🌾 Predicting Provincial Rice Yield in the Philippines

**COM241 Introduction to Machine Learning - Final Project**  
**Team:** Charles John R. Cabatian, Nico Andrew O. Gallardo, Renz Jerik C. Viloria  
**Instructor:** Dr. Armida P. Salazar  

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 📑 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Quick Start & Installation](#2-quick-start--installation)
3. [Project Structure](#3-project-structure)
4. [Data Dictionary & Sources](#4-data-dictionary--sources)
5. [Model Performance & Justification](#5-model-performance--justification)
6. [Application Guide (Streamlit)](#6-application-guide-streamlit)
7. [Reproducing Results](#7-reproducing-results)
8. [Testing & Validation](#8-testing--validation)
9. [Known Limitations](#9-known-limitations)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Project Overview
This project predicts province-level average rice yield (MT/ha) in the Philippines using fertilizer application, climate conditions, and simulated soil pH data. 

- **Problem Type:** Supervised Regression
- **Target Variable:** `yield_mt_ha` (Average palay yield in metric tons per hectare)
- **Dataset:** ~287 rows (province × season × ecosystem), covering 76 provinces across 2021 Semester 2 and 2022 Semester 1.
- **Scope:** Historical, province-level, Philippines-only data. Intended as an illustrative decision-support tool for agricultural extension workers or students, not a commercial production tool.
- **Why ML:** Yield response to combined fertilizer, rainfall, temperature, and soil pH involves interacting, non-linear effects that a single fixed formula cannot easily capture.

---

## 2. Quick Start & Installation

### Prerequisites
- **Python 3.10 or 3.11** (Newer versions may have compatibility issues with specific ML libraries).
- `pip` and `git` installed.

### Step-by-Step Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/projcjdevs/rice-yield-prediction.git
   cd rice-yield-prediction
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # macOS / Linux
   python3.11 -m venv .venv
   source .venv/bin/activate
   
   # Windows (PowerShell)
   py -3.11 -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   *(You will know it worked if your terminal prompt shows `(.venv)` at the start.)*

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Verify environment:**
   ```bash
   python -c "import pandas, numpy, sklearn, matplotlib, seaborn, streamlit, joblib, requests; print('✅ Environment OK')"
   ```

5. **Run the Streamlit App:**
   ```bash
   streamlit run app/app.py
   ```
   *The app will open in your default browser at `http://localhost:8501`.*

---

## 3. Project Structure
```text
rice-yield-prediction/
├── app/
│   └── app.py                  # Streamlit web application (Deployment)
├── artifacts/                  # Generated model artifacts (Contract 2)
│   ├── feature_order.json      # Exact ordered feature list for inference
│   ├── model_metrics.csv       # Evaluation metrics
│   ├── oof_predictions.csv     # Out-of-fold predictions
│   ├── test_predictions.csv    # Sealed test set predictions
│   └── split_provinces.json    # Train/test province split definition
├── data/
│   ├── processed/
│   │   ├── merged_rice_yield_dataset.csv  # Final modeling dataset
│   │   └── data_dictionary.md             # Detailed column descriptions
│   └── raw/                    # Raw source data (if applicable)
├── docs/                       # Planning documents and EDA figures
│   ├── figures/                # EDA visualizations
│   ├── 01_project_overview_and_architecture.md
│   ├── final_model_justification.md
│   └── eda_findings.md
├── image/                      # Streamlit app screenshots
│   ├── 1image.png              # App interface - Location & Season
│   ├── 2image.png              # App interface - Climate & Fertilizer
│   └── 3image.png              # App results - Prediction output
├── models/                     # Serialized artifacts (Contract 2)
│   ├── preprocessing_pipeline.joblib   # Fitted on training split only
│   ├── model_linear_baseline.joblib    # Baseline (reference only)
│   ├── model_ridge.joblib              # 🏆 SELECTED FINAL MODEL
│   ├── model_random_forest.joblib
│   └── model_gradient_boosting.joblib
├── notebooks/                  # Jupyter notebooks (Run in order 01 to 06)
│   ├── 01_eda.ipynb            # Exploratory Data Analysis
│   ├── 02_split.ipynb          # Train/Test Split (LOPO CV)
│   ├── 03_preprocess.ipynb     # Preprocessing Pipeline
│   ├── 04_augment.ipynb        # Mixup Augmentation
│   ├── 05_train.ipynb          # Model Training
│   └── 06_evaluate.ipynb       # Evaluation & Selection
├── src/                        # Shared source code
│   ├── data/                   # Data merging utilities
│   └── diagnostics/
│       └── extra_checks.py     # Post-hoc validation checks
├── tests/                      # Automated unit tests
│   ├── conftest.py             # Shared fixtures for pytest
│   ├── test_dataset_contract.py
│   └── test_model_inference.py
├── requirements.txt            # Python dependencies
├── SETUP.md                    # Detailed new-member onboarding guide
└── README.md                   # This file
```

---

## 4. Data Dictionary & Sources
A complete data dictionary is available in [`data/processed/data_dictionary.md`](data/processed/data_dictionary.md). 

**Key Features:**
| Column | Description | Source |
|--------|-------------|--------|
| `yield_mt_ha` | **Target:** Average palay yield (metric tons/ha) | PalayStat / PSA |
| `n_application_rate` | Nitrogen rate (assumed kg/ha) | PalayStat / Ricelytics |
| `p_application_rate` | Phosphorus rate (assumed kg/ha) | PalayStat / Ricelytics |
| `k_application_rate` | Potassium rate (assumed kg/ha) | PalayStat / Ricelytics |
| `rainfall_mm` | Semester total daily precipitation | NASA POWER / Open-Meteo |
| `temp_max_c` / `temp_min_c` | Mean daily max/min temperature over semester | NASA POWER / Open-Meteo |
| `solar_radiation_mj_m2` | Mean daily shortwave radiation over semester | NASA POWER / Open-Meteo |
| `soil_ph` | Fixed-seed simulated proxy per province/ecosystem | ISRIC SoilGrids |

*Note: `province` is retained for auditability and Leave-One-Province-Out (LOPO) grouping, but `island_group` is used as the geographic model feature to prevent overfitting. Source headers for fertilizer state "kg" without an explicit per-hectare denominator; treating these as `kg/ha` is an assumption based on plausible magnitudes.*

---

## 5. Model Performance & Justification
Based on Leave-One-Province-Out Cross-Validation (LOPO CV) over 60 training provinces, **Ridge Regression with 3x Stratified Mixup Augmentation** was selected as the final model *prior* to any test-set evaluation.

### Validation Evidence (Mixup 3x)
| Model | RMSE (Primary) | MAE | R² |
|-------|----------------|-----|----|
| **Ridge Regression** 🏆 | **0.6669** | **0.5405** | **0.3865** |
| Random Forest | 0.6838 | 0.5385 | 0.3548 |
| LightGBM / Gradient Boosting | 0.6912 | 0.5443 | 0.3409 |
| Linear Regression (Baseline) | 0.6681 | 0.5414 | 0.3842 |

**Rationale for Selection:**
1. **Primary Metric:** Achieves the lowest pooled Out-Of-Fold (OOF) RMSE.
2. **Interpretability:** Provides linear coefficients critical for provincial agricultural analysis, outweighing the marginal MAE advantage of Random Forest.
3. **Robustness:** Exhibits a tighter error profile, indicating fewer extreme outliers compared to tree-based models.

### Official Test Set Evaluation
The sealed test set (58 rows across 16 entirely unseen provinces) was evaluated exactly once.
- **Test RMSE:** 0.7022 (Falls squarely inside the validation bootstrap 95% CI `[0.6079, 0.7184]`, confirming no data leakage).
- **Test MAE:** 0.4747
- **Test R²:** 0.2818

*Note on Error Concentration:* Test error is highly concentrated in a single agro-ecological outlier province absent from the training set (Dinagat Islands, accounting for ~63% of total test squared error: actual ~2.0-2.2 t/ha vs predicted 3.7-4.7 t/ha). Excluding this province, the test RMSE drops to 0.4447, indicating the model is well-calibrated for provinces resembling the training distribution. See [`docs/final_model_justification.md`](docs/final_model_justification.md) for full details.

---

## 6. Application Guide (Streamlit)
Once the app is running (`streamlit run app/app.py`), follow these steps:

### 6.1 User Interface Walkthrough

**Step 1: Select Context (Location & Season)**
- Choose `Season Period` (2021_Semester_2 or 2022_Semester_1)
- Select `Ecosystem` (Irrigated or Non-irrigated)
- Pick `Island Group` (Luzon, Visayas, or Mindanao)

**Step 2: Configure Farm Area & Soil**
- Adjust `Area Harvested (ha)` using the slider or number input
- Modify `Soil pH (Simulated Proxy)` if needed (auto-populated based on province/ecosystem)

**Step 3: Input Climate Data (Semester Aggregates)**
- Set `Total Rainfall (mm)` for the semester
- Adjust `Solar Radiation (MJ/m²/day)`
- Configure `Mean Daily Max Temp (°C)` and `Mean Daily Min Temp (°C)`

**Step 4: Specify Fertilizer Application**
- Enter N, P, K application rates (kg/ha)
- Input quantities for top 5 fertilizer grades:
  - Urea (46-0-0)
  - Complete (14-14-14)
  - Ammophos (16-20-0)
  - Ammosul (21-0-0)
  - MOP (0-0-60)

**Step 5: Generate Prediction**
- Click the **"Predict Yield"** button
- View the estimated yield in both MT/ha and kg/ha
- Expand "Show derived model inputs" to see calculated features (Mean Temperature, Temperature Range, Total Fertilizer Mass, Diversification Index)

### 6.2 Application Screenshots

**Figure 1: Location, Season, and Farm Configuration**
![App Interface - Location & Season](image/1image.png)
*The main input panel showing location/season selection and farm area/soil configuration.*

**Figure 2: Climate and Fertilizer Inputs**
![App Interface - Climate & Fertilizer](image/2image.png)
*Climate parameters and detailed fertilizer application rates by grade.*

**Figure 3: Prediction Results**
![App Results - Prediction Output](image/3image.png)
*Estimated yield output with derived feature calculations displayed.*

### 6.3 Programmatic Inference Example
For developers or researchers who want to use the model outside the Streamlit app, the serialized artifacts in the `models/` and `artifacts/` directories can be loaded directly.

**Input Payload (JSON)**
```json
{
  "season_period": "2021_Semester_2",
  "ecosystem": "Irrigated",
  "island_group": "Luzon",
  "area_harvested_ha": 5000.0,
  "soil_ph": 5.8,
  "rainfall_mm": 1500.0,
  "solar_radiation_mj_m2": 17.5,
  "temp_max_c": 30.0,
  "temp_min_c": 23.0,
  "temp_mean_c": 26.5,
  "temp_range_c": 7.0,
  "n_application_rate": 75.0,
  "p_application_rate": 15.0,
  "k_application_rate": 15.0,
  "grade_urea_46_0_0_kg_ha": 80.0,
  "grade_complete_14_14_14_kg_ha": 70.0,
  "grade_ammophos_16_20_0_kg_ha": 15.0,
  "grade_ammosul_21_0_0_kg_ha": 10.0,
  "grade_mop_0_0_60_kg_ha": 5.0,
  "total_fertilizer_kg_ha": 180.0,
  "fertilizer_diversification_index": 1.195
}
```

**Python Implementation Snippet**
```python
import joblib
import pandas as pd
import json

# 1. Load the serialized artifacts
pipeline = joblib.load('models/preprocessing_pipeline.joblib')
model = joblib.load('models/model_ridge.joblib')

# 2. Load the exact feature order expected by the model
with open('artifacts/feature_order.json', 'r') as f:
    feature_order = json.load(f)

# 3. Prepare your input data as a Pandas DataFrame
input_data = pd.DataFrame([{
    "season_period": "2021_Semester_2",
    "ecosystem": "Irrigated",
    "island_group": "Luzon",
    "area_harvested_ha": 5000.0,
    "soil_ph": 5.8,
    "rainfall_mm": 1500.0,
    "solar_radiation_mj_m2": 17.5,
    "temp_max_c": 30.0,
    "temp_min_c": 23.0,
    "temp_mean_c": 26.5,
    "temp_range_c": 7.0,
    "n_application_rate": 75.0,
    "p_application_rate": 15.0,
    "k_application_rate": 15.0,
    "grade_urea_46_0_0_kg_ha": 80.0,
    "grade_complete_14_14_14_kg_ha": 70.0,
    "grade_ammophos_16_20_0_kg_ha": 15.0,
    "grade_ammosul_21_0_0_kg_ha": 10.0,
    "grade_mop_0_0_60_kg_ha": 5.0,
    "total_fertilizer_kg_ha": 180.0,
    "fertilizer_diversification_index": 1.195
}])

# 4. Pass the raw DataFrame directly to the pipeline.
# The ColumnTransformer automatically selects and transforms the correct raw columns.
X_processed = pipeline.transform(input_data)
prediction_mt_ha = model.predict(X_processed)

print(f"Predicted Yield: {prediction_mt_ha[0]:.2f} MT/ha")
print(f"Predicted Yield: {prediction_mt_ha[0] * 1000:.0f} kg/ha")
```

---

## 7. Reproducing Results
To ensure full reproducibility, execute the pipeline in the exact order below. 

**Option A: Automated Diagnostic Check**
```bash
python src/diagnostics/extra_checks.py --out artifacts/extra_checks_results.json
```

**Option B: Manual Notebook Execution**
Run the Jupyter notebooks in the `notebooks/` directory in this strict order:
1. `01_eda.ipynb` (Exploratory Data Analysis)
2. `02_split.ipynb` (Leave-One-Province-Out Split)
3. `03_preprocess.ipynb` (Fits preprocessing pipeline on train data *only*)
4. `04_augment.ipynb` (Applies 3x Stratified Mixup)
5. `05_train.ipynb` (Trains all 4 models, saves `.joblib` files to `models/`)
6. `06_evaluate.ipynb` (Generates metrics, saves to `artifacts/`)

---

## 8. Testing & Validation
To ensure software engineering rigor and model reliability, this project includes both automated unit tests and manual deployment edge-case testing.

### 8.1 Automated Unit Tests (Pytest)
We use `pytest` to validate data contracts and pipeline consistency.
**Test Coverage:**
1. `test_contract_1_dataset_is_complete_and_valid`: Ensures the dataset has all 21 required columns, exactly 287 rows, and valid physical ranges (e.g., soil pH between 4.0-8.0).
2. `test_model_inference_shape_and_type`: Verifies the preprocessing pipeline and Ridge model accept raw inputs and return a numeric prediction within realistic bounds (1.0 - 8.0 MT/ha).
3. `test_feature_order_matches_model`: Confirms the saved `feature_order.json` matches the number of coefficients in the trained model.

**Run Tests:**
```bash
pip install pytest
$env:PYTHONPATH="."; pytest tests/ -v
```

### 8.2 Deployment & Edge-Case Test Log
The Streamlit application (`app/app.py`) was manually tested against various edge cases to ensure robustness.

| # | Scenario | Inputs (Key variations) | Expected Behavior | Actual Result | Status |
|---|---|---|---|---|---|
| **1** | **Baseline (Happy Path)** | Luzon, Irrigated, S2, Avg Fertilizer (180 kg/ha total) | Prediction renders cleanly in the ~3.5-4.5 t/ha range. | Yield: ~4.1 t/ha. Derived inputs calculated correctly. | **PASS** |
| **2** | **Zero Fertilizer (Entropy Edge)** | All 5 grades = 0, N/P/K = 0 | Div. Index = 0.0. Prediction should drop. No division-by-zero crash. | Yield: 3.68 t/ha. Div Index: 0.0. No crash. | **PASS** |
| **3** | **Single Grade (Entropy = 0)** | Urea = 200, all other 4 grades = 0 | Div. Index = 0.0. Prediction should rise (200 > 180 total). | Yield: 4.68 t/ha. Div Index: -0.00 (IEEE 754 artifact). | **PASS** |
| **4** | **Extreme Area (Log1p Stress)** | Area = 150,000 ha (matches EDA max) | `log1p` squashes the tail. Prediction should be higher. | Yield: 4.97 t/ha. Correctly scaled without overflow. | **PASS** |
| **5** | **Tiny Area (Log1p Floor)** | Area = 10 ha, Visayas Non-irrigated | Prediction should drop significantly. | Yield: 3.62 t/ha. Correctly lower than baseline. | **PASS** |
| **6** | **Extreme Rainfall** | Rainfall = 3500 mm (EDA max) | Prediction renders. Rainfall correlation is weak, so yield shouldn't plummet. | Yield: 4.33 t/ha. Renders cleanly, no overflow. | **PASS** |
| **7** | **Invalid Temp Range** | Max Temp = 20°C, Min Temp = 25°C (Min > Max) | App accepts it. Model processes negative range (-5.0). | Yield: 3.17 t/ha. No crash. Temp range correctly calculated as -5.0°C. | **PASS*** |
| **8** | **Different Stratum** | Mindanao, Non-irrigated, S1 | Yield should be noticeably lower than Luzon Irrigated. | Yield: 3.12 t/ha. Correctly reflects non-irrigated penalty. | **PASS** |

*\*Note on Test 7: The app currently lacks client-side validation to enforce `temp_min <= temp_max`. While the Ridge model handles the negative feature value gracefully without crashing, a production deployment would add a Streamlit `st.error` guard for this physical impossibility.*

**Key Observations:**
1. **Model Consistency:** Predictions perfectly mirror EDA findings (e.g., increasing area/fertilizer increases yield; non-irrigated decreases it).
2. **Feature Engineering Integrity:** The app successfully replicates complex derivations (Shannon entropy, mean/range temperature) without user intervention.
3. **Edge Case Robustness:** The `log1p` transformation handled extreme areas gracefully, and entropy logic safely handled the 0 kg/ha edge case.

---

## 9. Known Limitations
1. **Small Dataset Size:** The dataset consists of only approximately 287 province-ecosystem-season observations across two season-years (2021 Semester 2 and 2022 Semester 1) covering 76 provinces. This limited sample size restricts the model's ability to capture long-term climate variability and may constrain generalization to unseen agro-ecological conditions.
2. **Simulated Soil pH:** Soil pH values are modeled proxies from ISRIC SoilGrids, not direct farm-level measurements. It primarily encodes ecosystem differences rather than independent soil chemistry.
3. **Fertilizer Unit Assumption:** Source headers state "kg" without an explicit per-hectare denominator. Treating these values as `kg/ha` is an assumption based on plausible magnitudes, not a confirmed source unit.
4. **Hyperparameters:** Ridge alpha and tree hyperparameters were not extensively tuned, adhering to the course's focus on baseline comparison and preprocessing over grid-search optimization.
5. **Area Harvested:** Known only *after* harvest, limiting real-time pre-season prediction capability.

---

## 10. Troubleshooting

| Issue | Solution |
|-------|----------|
| `pip install` fails on specific packages | Ensure you are using **Python 3.10 or 3.11**. Check `python --version`. |
| Virtual environment not activating | On Windows, run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell first. |
| Streamlit port already in use | Run `streamlit run app/app.py --server.port 8502` to use an alternate port. |
| SoilGrids API returns errors | ISRIC's live REST API is intermittently paused. The code includes a fallback; if it fails, check `docs/01_project_overview_and_architecture.md` for the static raster download alternative. |
| Pytest fails with `ModuleNotFoundError` | Ensure you run pytest from the project root and set `$env:PYTHONPATH="."` in PowerShell. |

---

## 🙏 Acknowledgments
- **Data Sources:** Philippine Statistics Authority (PalayStat), Ricelytics, NASA POWER / Open-Meteo, and ISRIC SoilGrids.
- **Course:** COM241 Introduction to Machine Learning.

*For detailed architectural decisions, task delegation, and contracts, please refer to the [`docs/`](docs/) directory.*