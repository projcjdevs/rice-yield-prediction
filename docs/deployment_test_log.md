# Deployment Test Log

## Environment & Setup
- **Execution:** Local Streamlit application (`streamlit run app/app.py`)
- **Framework:** Streamlit v1.65.0
- **Model:** Ridge Regression (trained on 229 real + 458 synthetic rows via Mixup 3x)
- **Preprocessing:** Scikit-learn ColumnTransformer (log1p area, standard scaling, one-hot drop='first')

## Test Cases & Results

| # | Scenario | Inputs (Key variations) | Expected Behavior | Actual Result | Status |
|---|---|---|---|---|---|
| **1** | **Baseline (Happy Path)** | Luzon, Irrigated, S2, Avg Fertilizer (180 kg/ha total) | Prediction renders cleanly in the ~3.5-4.5 t/ha range. | Yield: ~4.1 t/ha (Baseline). Derived inputs calculated correctly. | **PASS** |
| **2** | **Zero Fertilizer (Entropy Edge)** | All 5 grades = 0, N/P/K = 0 | Div. Index = 0.0. Prediction should drop (fertilizer r=0.353). No division-by-zero crash. | Yield: 3.68 t/ha (Correctly lower than baseline). Div Index: 0.0. No crash. | **PASS** |
| **3** | **Single Grade (Entropy = 0)** | Urea = 200, all other 4 grades = 0 | Div. Index = 0.0 (perfectly concentrated). Prediction should rise (200 > 180 total). | Yield: 4.68 t/ha. Div Index: -0.00. (Note: `-0.00` is a valid IEEE 754 floating-point artifact of `-1 * 0.0 * log(1.0)`). | **PASS** |
| **4** | **Extreme Area (Log1p Stress)** | Area = 150,000 ha (matches EDA max) | `log1p` squashes the tail. Prediction should be higher than baseline (area r=0.437). | Yield: 4.97 t/ha. Correctly scaled without overflow. | **PASS** |
| **5** | **Tiny Area (Log1p Floor)** | Area = 10 ha, Visayas Non-irrigated | Prediction should drop significantly. | Yield: 3.62 t/ha. Correctly lower than baseline. | **PASS** |
| **6** | **Extreme Rainfall** | Rainfall = 3500 mm (EDA max) | Prediction renders. Rainfall correlation is weak (-0.112), so yield shouldn't plummet. | Yield: 4.33 t/ha. Renders cleanly, no overflow. | **PASS** |
| **7** | **Invalid Temp Range** | Max Temp = 20°C, Min Temp = 25°C (Min > Max) | App accepts it (no client-side validation). Model processes negative range (-5.0). | Yield: 3.17 t/ha. No crash. Temp range correctly calculated as -5.0°C. | **PASS*** |
| **8** | **Different Stratum** | Mindanao, Non-irrigated, S1 | Yield should be noticeably lower than Luzon Irrigated (ecosystem gap is ~0.9 t/ha). | Yield: 3.12 t/ha. Div Index: 1.172. Correctly reflects non-irrigated penalty. | **PASS** |

*\*Note on Test 7: The app currently lacks client-side validation to enforce `temp_min <= temp_max`. While the Ridge model handles the negative feature value gracefully without crashing, a production deployment would add a Streamlit `st.error` guard for this physical impossibility.*

## Key Observations for the Final Paper
1. **Model Consistency:** The app's predictions perfectly mirror the EDA findings. Increasing area and fertilizer reliably increased yield, while switching to non-irrigated reliably decreased it.
2. **Feature Engineering Integrity:** The app successfully replicates Member 1's complex derivations (Shannon entropy for diversification, mean/range for temperature) without requiring the user to do the math.
3. **Edge Case Robustness:** The `log1p` transformation handled the extreme 150,000 ha area gracefully, and the entropy logic safely handled the 0 kg/ha edge case without throwing mathematical errors.