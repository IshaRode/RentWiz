"""
RentWiz – Pydantic Schemas: Property
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional


# ─── Input Schemas ─────────────────────────────────────────────────────────────

class PropertyFeatures(BaseModel):
    """Input features for rent prediction."""
    city: str = Field(..., example="Mumbai", description="City name")
    bhk: int = Field(..., ge=1, le=10, example=2, description="Number of bedrooms")
    area_sqft: int = Field(..., ge=100, le=10000, example=900, description="Area in sq ft")
    furnishing: Literal["Furnished", "Semi-Furnished", "Unfurnished"] = Field(
        default="Semi-Furnished", example="Semi-Furnished"
    )
    bathrooms: int = Field(default=1, ge=1, le=10, example=2)


class PropertyWithRent(PropertyFeatures):
    """Property features + actual listed rent (for /analyze endpoint)."""
    actual_rent: int = Field(..., ge=0, example=25000, description="Actual listed rent in INR/month")
    listing_url: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None   # sub-locality within city


# ─── Output Schemas ─────────────────────────────────────────────────────────────

class PredictResponse(BaseModel):
    predicted_rent: int
    city: str
    bhk: int
    area_sqft: int
    furnishing: str
    bathrooms: int
    confidence_note: str = "Based on GradientBoosting model trained on Indian rental data"


class AreaStats(BaseModel):
    city: str
    avg_rent: Optional[int] = None
    median_rent: Optional[int] = None
    min_rent: Optional[int] = None
    max_rent: Optional[int] = None
    total_listings: int = 0
    good_deals_count: int = 0
    fair_count: int = 0
    overpriced_count: int = 0
    trend_data: list[dict] = []
