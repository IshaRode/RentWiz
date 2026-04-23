"""
RentWiz – Supabase Seeder
Seeds 500 real ML-scored listings from the training CSV into Supabase.
Run: python scripts/seed_supabase.py
"""
import os
import sys
import random
import logging
import hashlib
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# ── Path setup so we can import from app/ ────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv(Path(__file__).parent.parent / ".env")

from app.services.prediction import predict_rent, load_model
from app.services.deal_scorer import classify_deal, compute_deal_pct

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

LOCATIONS_MAP = {
    "Mumbai":    ["Andheri West", "Bandra", "Powai", "Malad", "Goregaon", "Borivali"],
    "Delhi":     ["Lajpat Nagar", "Saket", "Dwarka", "Rohini", "Vasant Kunj", "Pitampura"],
    "Bangalore": ["Koramangala", "Indiranagar", "HSR Layout", "Whitefield", "BTM Layout", "Hebbal"],
    "Hyderabad": ["Banjara Hills", "Hitech City", "Madhapur", "Gachibowli", "Jubilee Hills"],
    "Pune":      ["Kothrud", "Baner", "Hinjewadi", "Wakad", "Viman Nagar", "Hadapsar"],
    "Chennai":   ["Anna Nagar", "Velachery", "Adyar", "Thoraipakkam", "Porur", "OMR"],
    "Kolkata":   ["Salt Lake", "Park Street", "Ballygunge", "Howrah", "Rajarhat"],
    "Ahmedabad": ["Satellite", "Prahlad Nagar", "Vastrapur", "Bopal", "SG Highway"],
    "Jaipur":    ["Malviya Nagar", "Mansarovar", "Vaishali Nagar", "C Scheme", "Tonk Road"],
    "Surat":     ["Adajan", "Vesu", "Piplod", "Varachha", "City Light"],
}


def seed_database(limit: int = 500):
    supabase_url = os.environ.get("SUPABASE_URL", "")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY", "")

    if not supabase_url or supabase_url == "https://your-project.supabase.co":
        logger.error("❌ SUPABASE_URL not set in backend/.env")
        return

    from supabase import create_client
    db = create_client(supabase_url, supabase_key)

    # Load the trained ML pipeline
    logger.info("Loading ML model...")
    load_model()

    # Load the training dataset
    csv_path = Path(__file__).parent.parent / "ml" / "data" / "house_rent.csv"
    if not csv_path.exists():
        logger.error(f"❌ Dataset not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    df = df.dropna()
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    df = df.head(limit)
    logger.info(f"Loaded {len(df)} rows — seeding to Supabase...")

    rng = random.Random(42)
    batch = []
    skipped = 0

    for i, row in df.iterrows():
        try:
            city        = str(row["City"]).strip()
            bhk         = int(row["BHK"])
            area        = int(row["Size"])
            furnishing  = str(row["Furnishing Status"]).strip()
            bathrooms   = int(row["Bathroom"])

            # actual_rent: real CSV rent ± 10% to simulate live listing variance
            actual_rent = max(3000, int(row["Rent"] * rng.uniform(0.90, 1.10) / 100) * 100)

            location = rng.choice(LOCATIONS_MAP.get(city, ["City Center"]))

            # ── Real ML prediction ───────────────────────────────────────────
            predicted_rent = predict_rent(
                city=city, bhk=bhk, area_sqft=area,
                furnishing=furnishing, bathrooms=bathrooms,
            )

            # ── Deal scoring ─────────────────────────────────────────────────
            deal_pct   = compute_deal_pct(predicted_rent, actual_rent)
            deal_score_val = predicted_rent - actual_rent
            deal_label = classify_deal(deal_score_val)

            url_hash = hashlib.md5(f"seed-{city}-{bhk}-{area}-{i}".encode()).hexdigest()

            # NOTE: do NOT include deal_score — it's a GENERATED column in Postgres
            listing = {
                "url_hash":       url_hash,
                "listing_url":    f"https://rentwiz.app/listing/{url_hash}",
                "title":          f"{bhk}BHK Apartment in {location}",
                "location":       location,
                "city":           city,
                "bhk":            bhk,
                "area_sqft":      area,
                "furnishing":     furnishing,
                "bathrooms":      bathrooms,
                "actual_rent":    actual_rent,
                "predicted_rent": predicted_rent,
                "deal_pct":       round(deal_pct, 2),
                "deal_label":     deal_label,
                "ai_explanation": _template_explanation(city, bhk, location, actual_rent, predicted_rent, deal_score_val, deal_label),
            }
            batch.append(listing)

        except Exception as e:
            skipped += 1
            logger.warning(f"Row {i} skipped: {e}")
            continue

        # Insert in batches of 50
        if len(batch) >= 50:
            _upsert_batch(db, batch)
            batch = []

    if batch:
        _upsert_batch(db, batch)

    logger.info(f"✅ Done! Seeded {len(df) - skipped} listings ({skipped} skipped).")


def _upsert_batch(db, batch: list):
    try:
        db.table("scraped_listings").upsert(batch, on_conflict="url_hash").execute()
        logger.info(f"  Inserted batch of {len(batch)}")
    except Exception as e:
        logger.error(f"  Batch insert failed: {e}")


def _template_explanation(city, bhk, location, actual, predicted, score, label):
    diff = abs(score)
    pct  = round(abs(score) / predicted * 100) if predicted else 0
    if label == "good_deal":
        return f"This {bhk}BHK in {location}, {city} is priced ₹{diff:,}/month below market — {pct}% savings vs comparable properties."
    elif label == "overpriced":
        return f"This {bhk}BHK in {location}, {city} is listed ₹{diff:,}/month above comparable properties. Worth negotiating."
    return f"This {bhk}BHK in {location}, {city} is fairly priced within ₹{diff:,}/month of the market rate."


if __name__ == "__main__":
    seed_database(limit=500)
