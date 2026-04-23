"""
RentWiz – POST /analyze
Full deal analysis: predict rent + score the deal + generate AI explanation.
"""
from fastapi import APIRouter, HTTPException
from app.schemas.property import PropertyWithRent
from app.schemas.deal import DealResult
from app.services.prediction import predict_rent
from app.services.deal_scorer import score_property
from app.services.ai_explainer import generate_explanation
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=DealResult, summary="Full deal analysis")
async def analyze(prop: PropertyWithRent):
    """
    Analyse a specific rental listing and return a complete deal assessment.

    Returns:
    - **predicted_rent**: Model's estimate of fair market rent
    - **deal_score**: predicted_rent – actual_rent (positive = underpriced)
    - **deal_label**: good_deal / fair / overpriced
    - **ai_explanation**: Plain-English explanation of the deal
    """
    try:
        predicted = predict_rent(
            city=prop.city,
            bhk=prop.bhk,
            area_sqft=prop.area_sqft,
            furnishing=prop.furnishing,
            bathrooms=prop.bathrooms,
        )

        scoring = score_property(predicted, prop.actual_rent)

        explanation = generate_explanation(
            city=prop.city,
            bhk=prop.bhk,
            area_sqft=prop.area_sqft,
            actual_rent=prop.actual_rent,
            predicted_rent=predicted,
            deal_score=scoring["deal_score"],
            deal_label=scoring["deal_label"],
            location=prop.location or "",
        )

        return DealResult(
            title=prop.title,
            location=prop.location,
            city=prop.city,
            bhk=prop.bhk,
            area_sqft=prop.area_sqft,
            furnishing=prop.furnishing,
            bathrooms=prop.bathrooms,
            actual_rent=prop.actual_rent,
            ai_explanation=explanation,
            listing_url=prop.listing_url,
            **scoring,
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
