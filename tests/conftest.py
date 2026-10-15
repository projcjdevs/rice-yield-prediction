import sys
from pathlib import Path
import joblib
import json
import pytest

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent

# Add root dir to sys.path in case you need to import from src later
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture(scope="session")
def model_pipeline():
    """Load the fitted preprocessing pipeline."""
    return joblib.load(ROOT_DIR / "models" / "preprocessing_pipeline.joblib")

@pytest.fixture(scope="session")
def trained_model():
    """Load the final trained Ridge model."""
    return joblib.load(ROOT_DIR / "models" / "model_ridge.joblib")

@pytest.fixture(scope="session")
def feature_order():
    """Load the expected feature order."""
    # Changed from "models" to "artifacts"
    with open(ROOT_DIR / "artifacts" / "feature_order.json", "r") as f:
        return json.load(f)