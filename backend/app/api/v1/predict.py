"""
RentWiz – POST /predict
Accepts property features and returns predicted fair market rent.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.property import PropertyFeatures, PredictResponse
from app.services.prediction import predict_rent
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/predict", response_model=PredictResponse, summary="Predict fair market rent")
async def predict(features: PropertyFeatures):
    """
    Predict the fair market rent for a property based on its features.

    - **city**: Target city (e.g., Mumbai, Delhi, Bangalore)
    - **bhk**: Number of bedrooms (1–10)
    - **area_sqft**: Total area in sq ft (100–10000)
    - **furnishing**: Furnished / Semi-Furnished / Unfurnished
    - **bathrooms**: Number of bathrooms
    """
    try:
        predicted = predict_rent(
            city=features.city,
            bhk=features.bhk,
            area_sqft=features.area_sqft,
            furnishing=features.furnishing,
            bathrooms=features.bathrooms,
        )
        return PredictResponse(
            predicted_rent=predicted,
            city=features.city,
            bhk=features.bhk,
            area_sqft=features.area_sqft,
            furnishing=features.furnishing,
            bathrooms=features.bathrooms,
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
