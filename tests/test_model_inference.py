import pytest
import pandas as pd
import numpy as np

def test_model_inference_shape_and_type(model_pipeline, trained_model):
    """Test that the model accepts valid raw input and returns a numeric prediction."""
    # 1. Create a single mock row with RAW column names (matching data_dictionary.md + derived features)
    mock_input = pd.DataFrame([{
        "season_period": "2021_Semester_2",
        "ecosystem": "Irrigated",
        "province": "Nueva Ecija",
        "island_group": "Luzon",
        "area_harvested_ha": 5000.0,
        "n_application_rate": 75.0,
        "p_application_rate": 15.0,
        "k_application_rate": 15.0,
        "grade_urea_46_0_0_kg_ha": 80.0,
        "grade_complete_14_14_14_kg_ha": 70.0,
        "grade_ammophos_16_20_0_kg_ha": 15.0,
        "grade_ammosul_21_0_0_kg_ha": 10.0,
        "grade_mop_0_0_60_kg_ha": 5.0,
        "total_fertilizer_kg_ha": 180.0,
        "fertilizer_diversification_index": 1.2,
        "rainfall_mm": 1500.0,
        "temp_max_c": 30.0,
        "temp_min_c": 23.0,
        "temp_mean_c": 26.5,     # <-- ADDED: (30.0 + 23.0) / 2
        "temp_range_c": 7.0,     # <-- ADDED: 30.0 - 23.0
        "solar_radiation_mj_m2": 17.5,
        "soil_ph": 5.8
    }])
    
    # 2. Pass the raw DataFrame directly to the pipeline.
    X_processed = model_pipeline.transform(mock_input)
    
    # 3. Predict
    prediction = trained_model.predict(X_processed)
    
    # 4. Assertions
    assert isinstance(prediction, np.ndarray), "Prediction should be a numpy array."
    assert len(prediction) == 1, "Prediction should return exactly one value for one row."
    
    pred_value = float(prediction[0])
    assert 1.0 <= pred_value <= 8.0, f"Prediction {pred_value} is outside realistic yield range (1.0 - 8.0 MT/ha)."

def test_feature_order_matches_model(trained_model, feature_order):
    """Test that the saved feature order matches the model's expected input size."""
    n_features_in_model = trained_model.coef_.shape[0]
    n_features_in_json = len(feature_order)
    
    assert n_features_in_json == n_features_in_model, \
        f"feature_order.json has {n_features_in_json} features, but model expects {n_features_in_model}."
    