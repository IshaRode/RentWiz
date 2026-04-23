"""
RentWiz – Prediction Service
Loads the full sklearn pipeline once at startup and exposes
a predict() function used by all API endpoints.
"""
import joblib
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ─── Module-level pipeline cache ────────────────────────────────────────────────
_pipeline = None
# Expose _model for health check compatibility
_model = None
_preprocessor = None


def load_model():
    """Load full pipeline from disk (called once at app startup)."""
    global _pipeline, _model, _preprocessor
    # Try full pipeline first (preferred)
    pipeline_path = Path("app/models/full_pipeline.joblib")
    model_path    = Path("app/models/rent_model.joblib")
    preprocessor_path = Path("app/models/preprocessor.joblib")

    if pipeline_path.exists():
        _pipeline = joblib.load(pipeline_path)
        # Set _model for health-check: use the GBR step
        _model = _pipeline.named_steps.get("model", _pipeline)
        _preprocessor = _pipeline.named_steps.get("preprocessor", None)
        logger.info(f"✅ Full pipeline loaded from {pipeline_path}")
    elif model_path.exists() and preprocessor_path.exists():
        _model = joblib.load(model_path)
        _preprocessor = joblib.load(preprocessor_path)
        logger.info(f"✅ Model + preprocessor loaded from {model_path}")
    else:
        logger.warning(
            "⚠️  No model found. Run `python ml/train.py` to train the model first."
        )


def predict_rent(
    city: str,
    bhk: int,
    area_sqft: int,
    furnishing: str = "Semi-Furnished",
    bathrooms: int = 1,
) -> int:
    """
    Predict fair market rent for a property.
    Returns predicted rent in INR/month (integer).
    Falls back to a heuristic estimate if model is unavailable.
    """
    if _pipeline is None and (_model is None or _preprocessor is None):
        logger.warning("Model not loaded – using heuristic fallback")
        return _heuristic_predict(city, bhk, area_sqft)

    input_df = pd.DataFrame([{
        "BHK": bhk,
        "Size": area_sqft,
        "City": city,
        "Furnishing Status": furnishing,
        "Bathroom": bathrooms,
    }])

    if _pipeline is not None:
        prediction = _pipeline.predict(input_df)[0]
    else:
        features = _preprocessor.transform(input_df)
        prediction = _model.predict(features)[0]

    return max(1000, int(round(prediction / 100) * 100))   # round to nearest ₹100


def _heuristic_predict(city: str, bhk: int, area_sqft: int) -> int:
    """Simple heuristic when model is unavailable."""
    base_rates = {
        "mumbai": 55, "delhi": 45, "bangalore": 40, "hyderabad": 35,
        "chennai": 32, "kolkata": 28, "pune": 35, "ahmedabad": 22,
    }
    rate = base_rates.get(city.lower(), 30)
    bhk_multiplier = {1: 0.8, 2: 1.0, 3: 1.3, 4: 1.7}.get(bhk, 1.0)
    return max(5000, int(rate * area_sqft * bhk_multiplier))
