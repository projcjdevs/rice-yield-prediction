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

# 1. Page Configuration
st.set_page_config(
    page_title="Philippine Rice Yield Estimator",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Paths & Constants
ROOT = Path(__file__).resolve().parents[1]
PREPROCESSING_PATH = ROOT / "models/preprocessing_pipeline.joblib"
MODEL_PATH = ROOT / "models/model_ridge.joblib"

# 3. Sidebar: Usage Guide & Context
with st.sidebar:
    st.header("🌾 How to Use This Tool")
    st.markdown("""
    This tool estimates average rice yield (palay) in metric tons per hectare (t/ha) based on location, climate, and farming practices.
    
    **Step-by-step:**
    1. Select your **Location & Season**.
    2. Enter your **Farm Area** and estimated **Soil pH**.
    3. Input **Climate** data for the semester (or use defaults).
    4. Enter your **Fertilizer Application** rates.
    5. Click **Predict Yield**.
    """)
    
    st.divider()
    st.header("⚠️ Important Notes")
    st.info("""
    - **Soil pH**: Uses simulated proxy data, not direct farm measurements.
    - **Fertilizer Units**: Inputs are assumed to be in kg/ha.
    - **Scope**: This model is trained on 2021-2022 data across 76 Philippine provinces. Predictions are estimates, not guarantees.
    """)

# 4. Load Artifacts
st.title("🌾 Philippine Rice Yield Estimator")
st.caption("Predicting provincial palay yield (t/ha) from agronomic, climate, and soil inputs. Survey-constrained demo (2021-2022 data window).")

artifacts_loaded = False
try:
    preprocessing = joblib.load(PREPROCESSING_PATH)
    model = joblib.load(MODEL_PATH)
    artifacts_loaded = True
except FileNotFoundError:
    st.error("🚨 **Model artifacts missing.**")
    st.markdown("""
    To fix this, ensure you have run the training notebooks or downloaded the artifacts.
    1. Open your terminal in the project root.
    2. Run: `python src/diagnostics/extra_checks.py --out artifacts/extra_checks_results.json`
    3. Or run notebooks `01_eda.ipynb` through `06_evaluate.ipynb`.
    """)

# 5. Form Inputs
with st.form("prediction_form"):
    st.subheader("1. Location & Season")
    col1, col2, col3 = st.columns(3)
    with col1:
        season_period = st.selectbox(
            "Season Period", 
            ["2021_Semester_2", "2022_Semester_1"],
            help="The cropping season for your prediction."
        )
    with col2:
        ecosystem = st.selectbox(
            "Ecosystem", 
            ["Irrigated", "Non-irrigated"],
            help="Irrigated fields typically have more stable, higher yields."
        )
    with col3:
        island_group = st.selectbox(
            "Island Group", 
            ["Luzon", "Visayas", "Mindanao"],
            help="Broad geographic region, which influences baseline climate and soil patterns."
        )

    st.subheader("2. Farm Area & Soil")
    col1, col2 = st.columns(2)
    with col1:
        area_harvested_ha = st.number_input(
            "Area Harvested (ha)", 
            min_value=1.0, 
            value=5000.0, 
            step=100.0,
            help="Total area of the farm harvested in hectares."
        )
    with col2:
        soil_ph = st.number_input(
            "Soil pH (Simulated Proxy)", 
            min_value=4.0, 
            max_value=8.5, 
            value=5.8, 
            step=0.1,
            help="Soil acidity/alkalinity. Values between 5.5 and 6.5 are generally optimal for rice."
        )

    st.subheader("3. Climate (Semester Aggregates)")
    st.markdown("*Enter average or total values for the entire cropping season.*")
    col1, col2 = st.columns(2)
    with col1:
        rainfall_mm = st.number_input(
            "Total Rainfall (mm)", 
            min_value=0.0, 
            value=1500.0, 
            step=50.0,
            help="Total precipitation during the semester."
        )
        temp_max_c = st.number_input(
            "Mean Daily Max Temp (°C)", 
            min_value=15.0,
            max_value=45.0,
            value=30.0, 
            step=0.5,
            help="Average of the daily maximum temperatures."
        )
    with col2:
        solar_radiation = st.number_input(
            "Solar Radiation (MJ/m²/day)", 
            min_value=0.0, 
            value=17.5, 
            step=0.5,
            help="Average daily shortwave radiation."
        )
        temp_min_c = st.number_input(
            "Mean Daily Min Temp (°C)", 
            min_value=10.0,
            max_value=35.0,
            value=23.0, 
            step=0.5,
            help="Average of the daily minimum temperatures."
        )

    # Input Validation for Temperature
    temp_warning = ""
    if temp_min_c > temp_max_c:
        temp_warning = "⚠️ **Warning:** Minimum temperature is higher than maximum temperature. The model will automatically swap these values for calculation."
        st.warning(temp_warning)
        # Swap for calculation to prevent pipeline errors
        actual_temp_max = temp_min_c
        actual_temp_min = temp_max_c
    else:
        actual_temp_max = temp_max_c
        actual_temp_min = temp_min_c

    st.subheader("4. Fertilizer Application (Assumed kg/ha)")
    st.markdown("*Enter the application rate for each nutrient and specific fertilizer grade used.*")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        n_rate = st.number_input("Nitrogen (N) Rate", min_value=0.0, value=75.0, step=1.0, help="kg/ha of pure Nitrogen")
    with col2:
        p_rate = st.number_input("Phosphorus (P) Rate", min_value=0.0, value=15.0, step=1.0, help="kg/ha of pure Phosphorus")
    with col3:
        k_rate = st.number_input("Potassium (K) Rate", min_value=0.0, value=15.0, step=1.0, help="kg/ha of pure Potassium")

    st.markdown("**Top 5 Fertilizer Grades Applied (kg/ha):**")
    col1, col2, col3 = st.columns(3)
    with col1:
        grade_urea = st.number_input("Urea (46-0-0)", min_value=0.0, value=80.0, step=1.0)
        grade_ammophos = st.number_input("Ammophos (16-20-0)", min_value=0.0, value=15.0, step=1.0)
    with col2:
        grade_complete = st.number_input("Complete (14-14-14)", min_value=0.0, value=70.0, step=1.0)
        grade_ammosul = st.number_input("Ammosul (21-0-0)", min_value=0.0, value=10.0, step=1.0)
    with col3:
        grade_mop = st.number_input("MOP (0-0-60)", min_value=0.0, value=5.0, step=1.0)

    submitted = st.form_submit_button("🌾 Predict Yield", type="primary", use_container_width=True)

# 6. Prediction Logic
if submitted:
    if not artifacts_loaded:
        st.error("Cannot predict. Model artifacts are missing. Please check the setup instructions in the sidebar.")
    else:
        # Derive temperature features (using corrected values if swapped)
        temp_mean_c = (actual_temp_max + actual_temp_min) / 2
        temp_range_c = actual_temp_max - actual_temp_min

        # Derive fertilizer features (exact math from build_features.py)
        grades = [grade_ammophos, grade_ammosul, grade_complete, grade_mop, grade_urea]
        total_fertilizer_kg_ha = sum(grades)

        if total_fertilizer_kg_ha > 0:
            shares = [g / total_fertilizer_kg_ha for g in grades]
            # Shannon entropy (handle 0 shares to avoid log(0))
            div_index = -sum(s * np.log(s) for s in shares if s > 0)
        else:
            div_index = 0.0

        # Input validation warnings for extreme values
        if total_fertilizer_kg_ha > 400:
            st.warning("⚠️ **High Fertilizer Alert:** Your total fertilizer input exceeds 400 kg/ha, which is unusually high and may lead to diminishing returns or environmental runoff. The model will still process this, but interpret the result with caution.")

        # Build the dataframe exactly matching the preprocessing pipeline
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
            st.divider()
            st.subheader("📊 Prediction Results")
            
            # Color-code the prediction based on typical Philippine yields
            if prediction < 2.5:
                st.metric("Estimated Yield", f"{prediction:.2f} t/ha", delta="Below Average", delta_color="inverse")
                st.info("This yield is below the typical Philippine average (3.0 - 4.0 t/ha). Consider reviewing irrigation, soil health, or fertilizer timing.")
            elif prediction < 4.5:
                st.metric("Estimated Yield", f"{prediction:.2f} t/ha", delta="Average to Good", delta_color="normal")
                st.success("This yield is within the typical, healthy range for Philippine rice production.")
            else:
                st.metric("Estimated Yield", f"{prediction:.2f} t/ha", delta="Excellent", delta_color="normal")
                st.success("This is an exceptionally high yield estimate, indicating optimal conditions and/or high input use.")

            st.caption(f"*(This equates to approximately {prediction * 1000:.0f} kg/ha)*")

            # SHAP-like Explanation (Simplified Feature Impact for Non-ML Users)
            st.subheader("💡 Understanding Your Prediction")
            st.markdown("Based on your inputs, here is how different factors typically influence this estimate:")
            
            impact_points = []
            if ecosystem == "Irrigated":
                impact_points.append("✅ **Irrigated Ecosystem**: Provides a stable baseline, typically resulting in higher yields compared to rainfed fields.")
            else:
                impact_points.append("⚠️ **Non-Irrigated Ecosystem**: Yields are more vulnerable to rainfall variability and drought.")
                
            if total_fertilizer_kg_ha > 150:
                impact_points.append("📈 **High Fertilizer Input**: Your total fertilizer application is above average, which generally supports higher yields, provided other conditions are optimal.")
            elif total_fertilizer_kg_ha < 50:
                impact_points.append("📉 **Low Fertilizer Input**: Your fertilizer application is below average, which may limit the maximum potential yield.")
                
            if div_index > 1.0:
                impact_points.append("🌱 **Diverse Fertilizer Mix**: Using multiple fertilizer grades (high diversification index) helps provide a balanced nutrient profile.")
            elif div_index == 0.0 and total_fertilizer_kg_ha > 0:
                impact_points.append("⚠️ **Single-Grade Fertilizer**: Relying on only one fertilizer grade may lead to nutrient imbalances over time.")

            if temp_range_c > 10:
                impact_points.append("🌡️ **High Temperature Variability**: A large difference between day and night temperatures can stress the crop, though rice is generally resilient.")

            for point in impact_points:
                st.markdown(f"- {point}")

            if not impact_points:
                st.markdown("- Your inputs represent a fairly standard, balanced farming scenario.")

            # Show derived values for transparency
            with st.expander("🔍 Show Technical Derived Inputs"):
                st.markdown("The model automatically calculates these features from your raw inputs:")
                st.write(f"- **Mean Temperature**: {temp_mean_c:.1f} °C")
                st.write(f"- **Temperature Range**: {temp_range_c:.1f} °C")
                st.write(f"- **Total Fertilizer Mass**: {total_fertilizer_kg_ha:.1f} kg/ha")
                st.write(f"- **Diversification Index (Shannon Entropy)**: {div_index:.3f}")
                st.caption("Note: The model uses a pre-fitted preprocessing pipeline to scale and encode these values before prediction.")

        except Exception as e:
            st.error(f"❌ **Prediction failed due to an unexpected error:**\n\n`{str(e)}`\n\nPlease check your inputs and ensure they are within realistic ranges. If the problem persists, contact the development team.")