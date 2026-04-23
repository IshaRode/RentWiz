"""
RentWiz – GET /best-deals
Returns top-ranked properties sorted by deal score (predicted - actual rent).

Data priority:
  1. Supabase: scraped listings (real MagicBricks URLs) — preferred
  2. Supabase: seeded listings (training CSV, no real URL) — fallback
  3. ML-scored demo data — if Supabase is not configured
"""
from fastapi import APIRouter, Query, HTTPException
from app.schemas.deal import BestDealsResponse, DealResult
from app.core.config import settings
from app.services.prediction import predict_rent
from app.services.deal_scorer import classify_deal, deal_label_display, compute_deal_pct
from app.services.ai_explainer import generate_explanation
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

DEMO_CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune", "Chennai"]
DEMO_LOCATIONS = {
    "Mumbai":    ["Andheri West", "Bandra", "Powai", "Malad", "Goregaon"],
    "Delhi":     ["Lajpat Nagar", "Saket", "Dwarka", "Rohini", "Vasant Kunj"],
    "Bangalore": ["Koramangala", "Indiranagar", "HSR Layout", "Whitefield", "BTM Layout"],
    "Hyderabad": ["Banjara Hills", "Hitech City", "Madhapur", "Gachibowli", "Jubilee Hills"],
    "Pune":      ["Kothrud", "Baner", "Hinjewadi", "Wakad", "Viman Nagar"],
    "Chennai":   ["Anna Nagar", "Velachery", "Adyar", "Thoraipakkam", "Porur"],
}
BASE_ACTUAL_RENTS = {
    "Mumbai": 32000, "Delhi": 22000, "Bangalore": 20000,
    "Hyderabad": 17000, "Pune": 17000, "Chennai": 15000,
}
FAKE_URL_MARKERS = ["rentwiz.app", "example.com", "/demo-", "mock/"]


def _is_real_url(url: str | None) -> bool:
    if not url:
        return False
    return not any(m in url for m in FAKE_URL_MARKERS)


def _generate_ml_demo_listings(city: str, bhk: int | None, limit: int) -> list[dict]:
    """
    Demo fallback: generates listings with REAL ML predictions when Supabase
    is not configured. actual_rent is simulated; predicted_rent is real ML output.
    """
    rng = random.Random(42)
    cities = [city] if city else DEMO_CITIES
    listings = []

    for i in range(limit * 3):
        c = rng.choice(cities)
        b = bhk if bhk else rng.choice([1, 2, 3])
        area = rng.randint(400 + b * 150, 600 + b * 300)
        furnishing = rng.choice(["Furnished", "Semi-Furnished", "Unfurnished"])
        bathrooms = min(b, 3)
        loc = rng.choice(DEMO_LOCATIONS.get(c, ["City Center"]))

        base = BASE_ACTUAL_RENTS.get(c, 18000)
        actual_rent = max(5000, int(base * b * 0.65 * rng.uniform(0.75, 1.30) / 100) * 100)

        try:
            predicted_rent = predict_rent(
                city=c, bhk=b, area_sqft=area,
                furnishing=furnishing, bathrooms=bathrooms,
            )
        except Exception:
            continue

        deal_score = predicted_rent - actual_rent
        deal_pct   = compute_deal_pct(predicted_rent, actual_rent)
        label      = classify_deal(deal_score)
        label_disp = deal_label_display(label)
        explanation = generate_explanation(
            city=c, bhk=b, area_sqft=area,
            actual_rent=actual_rent, predicted_rent=predicted_rent,
            deal_score=deal_score, deal_label=label, location=loc,
        )

        listings.append({
            "title":              f"{b}BHK Apartment in {loc}",
            "location":           loc,
            "city":               c,
            "bhk":                b,
            "area_sqft":          area,
            "furnishing":         furnishing,
            "bathrooms":          bathrooms,
            "actual_rent":        actual_rent,
            "predicted_rent":     predicted_rent,
            "deal_score":         deal_score,
            "deal_pct":           deal_pct,
            "deal_label":         label,
            "deal_label_display": label_disp,
            "ai_explanation":     explanation,
            "listing_url":        None,
            "scraped_at":         (datetime.now() - timedelta(hours=rng.randint(1, 48))).isoformat(),
        })

    listings.sort(key=lambda x: x["deal_score"], reverse=True)
    return listings[:limit]


@router.get("/best-deals", response_model=BestDealsResponse, summary="Get top-ranked rental deals")
async def best_deals(
    city:   str      = Query(default="",   description="Filter by city"),
    bhk:    int|None = Query(default=None, ge=1, le=10),
    label:  str|None = Query(default=None, description="good_deal / fair / overpriced"),
    limit:  int      = Query(default=20,   ge=1, le=100),
    offset: int      = Query(default=0,    ge=0),
):
    """
    Returns rental listings ranked by deal score (best deals first).
    Predicted rent always comes from the trained ML model.
    """
    try:
        # ── 1. Supabase path ────────────────────────────────────────────────
        if settings.supabase_url != "https://your-project.supabase.co":
            from app.core.database import get_supabase
            db = get_supabase()

            query = (
                db.table("scraped_listings")
                .select("*")
                .order("deal_score", desc=True)
            )
            if city:  query = query.eq("city", city)
            if bhk:   query = query.eq("bhk", bhk)
            if label: query = query.eq("deal_label", label)

            # Fetch a larger batch so we can separate scraped vs seeded in-memory
            result = query.limit(300).execute()
            all_rows = result.data or []

            # Separate real scraped (valid external URL) from seeded (placeholder URL)
            scraped_rows = [r for r in all_rows if _is_real_url(r.get("listing_url"))]
            seeded_rows  = [r for r in all_rows if not _is_real_url(r.get("listing_url"))]

            rows_to_use = scraped_rows if scraped_rows else seeded_rows
            rows_to_use = rows_to_use[offset: offset + limit]

            if rows_to_use:
                source_tag = "supabase_scraped" if scraped_rows else "supabase_seeded"
                listings = []
                for row in rows_to_use:
                    row["deal_label_display"] = deal_label_display(row.get("deal_label", "fair"))
                    listings.append(DealResult(**row))

                return BestDealsResponse(
                    listings=listings,
                    total=len(rows_to_use),
                    filters_applied={"city": city, "bhk": bhk, "label": label, "source": source_tag},
                )

        # ── 2. ML demo fallback ──────────────────────────────────────────────
        logger.info("Supabase not configured — using ML-scored demo listings")
        all_listings = _generate_ml_demo_listings(city or "", bhk, limit)
        if label:
            all_listings = [d for d in all_listings if d["deal_label"] == label]

        return BestDealsResponse(
            listings=[DealResult(**d) for d in all_listings[:limit]],
            total=len(all_listings),
            filters_applied={"city": city, "bhk": bhk, "label": label, "source": "ml_demo"},
        )

    except Exception as e:
        logger.error(f"/best-deals error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
