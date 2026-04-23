"""
RentWiz – Pydantic Schemas: Deal Scoring
"""
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


DealLabel = Literal["good_deal", "fair", "overpriced"]


class DealResult(BaseModel):
    """Full analysis result for a single property."""
    # Property details
    title: Optional[str] = None
    location: Optional[str] = None
    city: str
    bhk: int
    area_sqft: int
    furnishing: str
    bathrooms: int

    # Pricing
    actual_rent: int
    predicted_rent: int
    deal_score: int          # predicted_rent - actual_rent (positive = underpriced)
    deal_pct: float          # % saved vs predicted (positive = savings)

    # Classification
    deal_label: DealLabel
    deal_label_display: str  # Human-friendly label

    # AI
    ai_explanation: Optional[str] = None

    # Meta
    listing_url: Optional[str] = None
    scraped_at: Optional[datetime] = None


class BestDealsResponse(BaseModel):
    listings: list[DealResult]
    total: int
    filters_applied: dict


class AreaInsightsResponse(BaseModel):
    city: str
    avg_rent: int
    median_rent: int
    min_rent: int
    max_rent: int
    total_listings: int
    deal_distribution: dict  # {"good_deal": N, "fair": N, "overpriced": N}
    avg_deal_score: int
    top_localities: list[dict]
    rent_by_bhk: list[dict]  # [{"bhk": 1, "avg_rent": ...}, ...]
