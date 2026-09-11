"""
Member 3 — Deployment.

Loads the final selected model (one of ridge / random_forest / gradient_boosting —
per docs/01_project_overview_and_architecture.md §7, never linear_baseline) plus
the fitted preprocessing pipeline, and serves a simple prediction form.

Run with: streamlit run app/app.py
"""

import joblib
import pandas as pd
import streamlit as st

PREPROCESSING_PATH = "models/preprocessing_pipeline.joblib"
FINAL_MODEL_PATH = "models/model_gradient_boosting.joblib"  # update once the final model is chosen

st.title("Philippine Rice Yield Estimator")
st.caption("Illustrative decision-support demo — Intro to ML final project. Not for production use.")

try:
    preprocessing = joblib.load(PREPROCESSING_PATH)
    model = joblib.load(FINAL_MODEL_PATH)
    artifacts_loaded = True
except FileNotFoundError:
    artifacts_loaded = False
    st.warning(
        "Model artifacts not found yet. Run the training pipeline (Contract 2) "
        "first, or check that models/ contains the required .joblib files."
    )

with st.form("prediction_form"):
    province = st.text_input("Province")
    region = st.text_input("Region")
    year = st.number_input("Year", min_value=1990, max_value=2100, value=2026, step=1)
    season = st.selectbox("Season", ["wet", "dry"])
    area_harvested_ha = st.number_input("Area harvested (ha)", min_value=0.0, value=1.0)
    fertilizer_total_kg_ha = st.number_input("Fertilizer applied (kg/ha)", min_value=0.0, value=100.0)
    rainfall_mm = st.number_input("Rainfall (mm)", min_value=0.0, value=1500.0)
    avg_temp_c = st.number_input("Average temperature (°C)", value=27.0)
    solar_radiation = st.number_input("Solar radiation", value=15.0)
    humidity_pct = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=75.0)
    soil_ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=6.0)
    submitted = st.form_submit_button("Predict Yield")

if submitted:
    if not artifacts_loaded:
        st.error("Cannot predict — model artifacts are missing. See warning above.")
    else:
        input_df = pd.DataFrame([{
            "province": province, "region": region, "year": year, "season": season,
            "area_harvested_ha": area_harvested_ha,
            "fertilizer_total_kg_ha": fertilizer_total_kg_ha,
            "rainfall_mm": rainfall_mm, "avg_temp_c": avg_temp_c,
            "solar_radiation": solar_radiation, "humidity_pct": humidity_pct,
            "soil_ph": soil_ph,
        }])
        X = preprocessing.transform(input_df)
        prediction = model.predict(X)[0]
        st.success(f"Estimated yield: {prediction:,.0f} kg/ha")
