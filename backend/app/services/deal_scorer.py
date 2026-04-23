"""
RentWiz – Deal Scoring Service
Core algorithm: deal_score = predicted_rent - actual_rent
Positive = underpriced (good deal), negative = overpriced.
"""
from app.core.config import settings
from app.schemas.deal import DealLabel


def compute_deal_score(predicted_rent: int, actual_rent: int) -> int:
    """Return deal_score in INR (positive = savings, negative = premium)."""
    return predicted_rent - actual_rent


def compute_deal_pct(predicted_rent: int, actual_rent: int) -> float:
    """Return % difference relative to predicted rent.
    Positive = % below market, negative = % above market.
    """
    if predicted_rent == 0:
        return 0.0
    return round((predicted_rent - actual_rent) / predicted_rent * 100, 1)


def classify_deal(deal_score: int) -> DealLabel:
    """Classify a listing based on deal_score thresholds from config."""
    if deal_score >= settings.good_deal_threshold:
        return "good_deal"
    elif deal_score <= settings.overpriced_threshold:
        return "overpriced"
    else:
        return "fair"


def deal_label_display(label: DealLabel) -> str:
    return {
        "good_deal": "🟢 Great Deal",
        "fair": "🟡 Fair Price",
        "overpriced": "🔴 Overpriced",
    }[label]


def score_property(predicted_rent: int, actual_rent: int) -> dict:
    """
    Full deal scoring for a property.
    Returns a dict compatible with DealResult schema fields.
    """
    score = compute_deal_score(predicted_rent, actual_rent)
    pct = compute_deal_pct(predicted_rent, actual_rent)
    label = classify_deal(score)
    return {
        "predicted_rent": predicted_rent,
        "deal_score": score,
        "deal_pct": pct,
        "deal_label": label,
        "deal_label_display": deal_label_display(label),
    }
