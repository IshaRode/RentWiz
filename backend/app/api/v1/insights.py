"""
RentWiz – GET /area-insights
Computes REAL aggregations from scraped_listings in Supabase.
Falls back to ML-scored synthetic data if DB has no rows for that city.
"""
from fastapi import APIRouter, Query, HTTPException
from app.schemas.deal import AreaInsightsResponse
from app.core.config import settings
from app.services.prediction import predict_rent
from app.services.deal_scorer import classify_deal, compute_deal_pct
import logging
import statistics
import random

logger = logging.getLogger(__name__)
router = APIRouter()

_CITY_BASES = {
    "Mumbai":    {"base": 35000, "locs": ["Andheri West", "Bandra", "Powai", "Malad", "Goregaon", "Borivali"]},
    "Delhi":     {"base": 25000, "locs": ["Lajpat Nagar", "Saket", "Dwarka", "Rohini", "Vasant Kunj", "Pitampura"]},
    "Bangalore": {"base": 22000, "locs": ["Koramangala", "Indiranagar", "HSR Layout", "Whitefield", "BTM Layout", "Hebbal"]},
    "Hyderabad": {"base": 18000, "locs": ["Banjara Hills", "Hitech City", "Madhapur", "Gachibowli", "Jubilee Hills"]},
    "Pune":      {"base": 18000, "locs": ["Kothrud", "Baner", "Hinjewadi", "Wakad", "Viman Nagar", "Hadapsar"]},
    "Chennai":   {"base": 16000, "locs": ["Anna Nagar", "Velachery", "Adyar", "Thoraipakkam", "Porur", "OMR"]},
    "Kolkata":   {"base": 14000, "locs": ["Salt Lake", "Park Street", "Ballygunge", "Howrah", "Rajarhat"]},
    "Ahmedabad": {"base": 12000, "locs": ["Satellite", "Prahlad Nagar", "Vastrapur", "Bopal", "SG Highway"]},
}


def _aggregate_from_rows(city: str, rows: list[dict]) -> dict:
    """Compute real market statistics from a list of scraped_listing rows."""
    rents  = [r["actual_rent"] for r in rows if r.get("actual_rent")]
    labels = [r.get("deal_label", "fair") for r in rows]

    avg_rent    = int(statistics.mean(rents))    if rents else 0
    median_rent = int(statistics.median(rents))  if rents else 0
    min_rent    = min(rents)                      if rents else 0
    max_rent    = max(rents)                      if rents else 0

    good_deal  = labels.count("good_deal")
    fair       = labels.count("fair")
    overpriced = labels.count("overpriced")

    # BHK breakdown
    bhk_groups: dict[int, list[int]] = {}
    for r in rows:
        b = r.get("bhk")
        a = r.get("actual_rent")
        if b and a:
            bhk_groups.setdefault(b, []).append(a)
    rent_by_bhk = [
        {"bhk": bhk, "avg_rent": int(statistics.mean(vs)), "count": len(vs)}
        for bhk, vs in sorted(bhk_groups.items())
    ]

    # Locality breakdown
    loc_groups: dict[str, list[int]] = {}
    for r in rows:
        loc = r.get("location", "")
        a   = r.get("actual_rent")
        if loc and a:
            loc_groups.setdefault(loc, []).append(a)
    top_localities = sorted([
        {"location": loc, "avg_rent": int(statistics.mean(vs)), "listings": len(vs)}
        for loc, vs in loc_groups.items()
    ], key=lambda x: x["avg_rent"])[:8]

    deal_scores = [r.get("deal_score", 0) for r in rows if r.get("deal_score") is not None]
    avg_deal_score = int(statistics.mean(deal_scores)) if deal_scores else 0

    return {
        "city":             city,
        "avg_rent":         avg_rent,
        "median_rent":      median_rent,
        "min_rent":         min_rent,
        "max_rent":         max_rent,
        "total_listings":   len(rows),
        "deal_distribution": {"good_deal": good_deal, "fair": fair, "overpriced": overpriced},
        "avg_deal_score":   avg_deal_score,
        "top_localities":   top_localities,
        "rent_by_bhk":      rent_by_bhk,
    }


def _ml_fallback_insights(city: str) -> dict:
    """Generate ML-scored synthetic insights when DB has no data for this city."""
    rng  = random.Random(hash(city) % 9999)
    info = _CITY_BASES.get(city, {"base": 18000, "locs": ["City Center"]})
    base = info["base"]
    locs = info["locs"]
    furnishings = ["Furnished", "Semi-Furnished", "Unfurnished"]

    rows = []
    for _ in range(80):
        bhk        = rng.choice([1, 2, 3, 4])
        area       = rng.randint(400 + bhk * 100, 600 + bhk * 300)
        furnishing = rng.choice(furnishings)
        bathrooms  = min(bhk, 3)
        location   = rng.choice(locs)
        actual     = max(4000, int(base * bhk * 0.65 * rng.uniform(0.75, 1.25) / 100) * 100)

        try:
            predicted = predict_rent(city=city, bhk=bhk, area_sqft=area,
                                     furnishing=furnishing, bathrooms=bathrooms)
        except Exception:
            predicted = actual

        score = predicted - actual
        label = classify_deal(score)

        rows.append({
            "actual_rent":  actual,
            "deal_score":   score,
            "deal_label":   label,
            "bhk":          bhk,
            "location":     location,
        })

    return _aggregate_from_rows(city, rows)


@router.get("/area-insights", response_model=AreaInsightsResponse, summary="Area market insights")
async def area_insights(
    city: str = Query(..., description="City name e.g. Mumbai, Delhi, Bangalore"),
):
    """
    Returns aggregated rental market statistics for a city.
    Data comes from Supabase scraped_listings (real ML-scored data).
    Falls back to ML-scored synthetic data if no DB rows exist for that city.
    """
    try:
        # ── 1. Try Supabase ───────────────────────────────────────────────────
        if settings.supabase_url != "https://your-project.supabase.co":
            from app.core.database import get_supabase
            db = get_supabase()
            result = (
                db.table("scraped_listings")
                .select("actual_rent, predicted_rent, deal_score, deal_label, bhk, location")
                .eq("city", city)
                .limit(500)
                .execute()
            )
            rows = result.data or []

            if rows:
                logger.info(f"area-insights: {len(rows)} rows from Supabase for {city}")
                return AreaInsightsResponse(**_aggregate_from_rows(city, rows))

            logger.info(f"area-insights: No Supabase rows for {city} — using ML fallback")

        # ── 2. ML-scored fallback ─────────────────────────────────────────────
        return AreaInsightsResponse(**_ml_fallback_insights(city))

    except Exception as e:
        logger.error(f"area-insights error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
