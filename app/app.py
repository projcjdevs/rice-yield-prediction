"""
Member 3 — Deployment.
Streamlit app for predicting provincial rice yield using the final selected model
(Ridge Regression + Mixup 3x).
Run locally with: streamlit run app/app.py
"""

import joblib
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path

# 1. Paths
ROOT = Path(__file__).resolve().parents[1]
PREPROCESSING_PATH = ROOT / "models/preprocessing_pipeline.joblib"
MODEL_PATH = ROOT / "models/model_ridge.joblib"

# 2. Load Artifacts
st.title("Philippine Rice Yield Estimator")
st.caption("Predicting provincial palay yield (t/ha) from agronomic, climate, and soil inputs. Survey-constrained demo (2021-2022 data window).")

try:
    preprocessing = joblib.load(PREPROCESSING_PATH)
    model = joblib.load(MODEL_PATH)
    artifacts_loaded = True
except FileNotFoundError:
    artifacts_loaded = False
    st.error("Model artifacts missing. Ensure `models/preprocessing_pipeline.joblib` and `models/model_ridge.joblib` exist.")

# 3. Form Inputs
with st.form("prediction_form"):
    st.subheader("1. Location & Season")
    season_period = st.selectbox("Season Period", ["2021_Semester_2", "2022_Semester_1"])
    ecosystem = st.selectbox("Ecosystem", ["Irrigated", "Non-irrigated"])
    island_group = st.selectbox("Island Group", ["Luzon", "Visayas", "Mindanao"])

    st.subheader("2. Farm Area & Soil")
    area_harvested_ha = st.number_input("Area Harvested (ha)", min_value=0.0, value=5000.0, step=100.0)
    soil_ph = st.number_input("Soil pH (Simulated Proxy)", min_value=4.0, max_value=8.0, value=5.8, step=0.1)

    st.subheader("3. Climate (Semester Aggregates)")
    rainfall_mm = st.number_input("Total Rainfall (mm)", min_value=0.0, value=1500.0, step=50.0)
    solar_radiation = st.number_input("Solar Radiation (MJ/m²/day)", min_value=0.0, value=17.5, step=0.1)
    temp_max_c = st.number_input("Mean Daily Max Temp (°C)", value=30.0, step=0.1)
    temp_min_c = st.number_input("Mean Daily Min Temp (°C)", value=23.0, step=0.1)

    st.subheader("4. Fertilizer Application (Assumed kg/ha)")
    n_rate = st.number_input("Nitrogen (N) Rate", min_value=0.0, value=75.0, step=1.0)
    p_rate = st.number_input("Phosphorus (P) Rate", min_value=0.0, value=15.0, step=1.0)
    k_rate = st.number_input("Potassium (K) Rate", min_value=0.0, value=15.0, step=1.0)

    st.markdown("**Top 5 Fertilizer Grades Applied:**")
    grade_urea = st.number_input("Urea (46-0-0)", min_value=0.0, value=80.0, step=1.0)
    grade_complete = st.number_input("Complete (14-14-14)", min_value=0.0, value=70.0, step=1.0)
    grade_ammophos = st.number_input("Ammophos (16-20-0)", min_value=0.0, value=15.0, step=1.0)
    grade_ammosul = st.number_input("Ammosul (21-0-0)", min_value=0.0, value=10.0, step=1.0)
    grade_mop = st.number_input("MOP (0-0-60)", min_value=0.0, value=5.0, step=1.0)

    submitted = st.form_submit_button("Predict Yield")

# 4. Prediction Logic
if submitted:
    if not artifacts_loaded:
        st.error("Cannot predict. Artifacts missing.")
    else:
        # Derive temperature features
        temp_mean_c = (temp_max_c + temp_min_c) / 2
        temp_range_c = temp_max_c - temp_min_c

        # Derive fertilizer features (exact math from build_features.py)
        grades = [grade_ammophos, grade_ammosul, grade_complete, grade_mop, grade_urea]
        total_fertilizer_kg_ha = sum(grades)

        if total_fertilizer_kg_ha > 0:
            shares = [g / total_fertilizer_kg_ha for g in grades]
            # Shannon entropy (handle 0 shares to avoid log(0))
            div_index = -sum(s * np.log(s) for s in shares if s > 0)
        else:
            div_index = 0.0

        # Build the 14-column dataframe exactly matching the preprocessing pipeline
        input_df = pd.DataFrame([{
            "season_period": season_period,
            "ecosystem": ecosystem,
            "island_group": island_group,
            "area_harvested_ha": area_harvested_ha,
            "n_application_rate": n_rate,
            "p_application_rate": p_rate,
            "k_application_rate": k_rate,
            "total_fertilizer_kg_ha": total_fertilizer_kg_ha,
            "fertilizer_diversification_index": div_index,
            "rainfall_mm": rainfall_mm,
            "solar_radiation_mj_m2": solar_radiation,
            "soil_ph": soil_ph,
            "temp_mean_c": temp_mean_c,
            "temp_range_c": temp_range_c,
        }])

        try:
            # Transform and predict
            X = preprocessing.transform(input_df)
            prediction = model.predict(X)[0]

            # Display results
            st.success(f"**Estimated Yield:** {prediction:.2f} metric tons / hectare")
            st.info(f"*(This equates to approximately {prediction * 1000:.0f} kg/ha)*")

            # Show derived values for transparency
            with st.expander("Show derived model inputs"):
                st.write(f"- Mean Temperature: {temp_mean_c:.1f} °C")
                st.write(f"- Temperature Range: {temp_range_c:.1f} °C")
                st.write(f"- Total Fertilizer Mass: {total_fertilizer_kg_ha:.1f} kg/ha")
                st.write(f"- Diversification Index: {div_index:.3f}")

        except Exception as e:
            st.error(f"Prediction failed: {str(e)}")