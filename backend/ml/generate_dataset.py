"""
RentWiz – Kaggle House Rent Dataset Generator
Since we can't download from Kaggle directly, this script generates a
realistic synthetic dataset that mimics the real Kaggle House_Rent_Dataset.csv.

The real dataset is available at:
https://www.kaggle.com/datasets/iamsouravbanerjee/house-rent-prediction-dataset

If you have the Kaggle dataset, place it at: backend/ml/data/house_rent.csv
and this script will NOT overwrite it.

Usage:
    cd backend
    python ml/generate_dataset.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = Path(__file__).parent / "data" / "house_rent.csv"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

CITIES = {
    "Mumbai":    {"base_per_sqft": 52, "bhk_multiplier": 1.3},
    "Delhi":     {"base_per_sqft": 42, "bhk_multiplier": 1.2},
    "Bangalore": {"base_per_sqft": 38, "bhk_multiplier": 1.15},
    "Hyderabad": {"base_per_sqft": 32, "bhk_multiplier": 1.1},
    "Pune":      {"base_per_sqft": 33, "bhk_multiplier": 1.1},
    "Chennai":   {"base_per_sqft": 29, "bhk_multiplier": 1.05},
    "Kolkata":   {"base_per_sqft": 24, "bhk_multiplier": 1.0},
    "Ahmedabad": {"base_per_sqft": 20, "bhk_multiplier": 0.95},
    "Jaipur":    {"base_per_sqft": 18, "bhk_multiplier": 0.9},
    "Surat":     {"base_per_sqft": 17, "bhk_multiplier": 0.88},
}

FURNISHING_MULTIPLIER = {
    "Furnished":       1.25,
    "Semi-Furnished":  1.0,
    "Unfurnished":     0.82,
}

POINT_OF_CONTACT = ["Contact Owner", "Contact Agent", "Contact Builder"]
AREA_LOCALITY = {
    "Mumbai": ["Andheri West", "Bandra East", "Powai", "Malad West", "Goregaon East",
               "Borivali West", "Kandivali East", "Kurla West", "Thane", "Navi Mumbai"],
    "Delhi": ["Lajpat Nagar", "Saket", "Dwarka", "Rohini", "Vasant Kunj",
              "Janakpuri", "Pitampura", "Uttam Nagar", "Mayur Vihar", "Patel Nagar"],
    "Bangalore": ["Koramangala", "Indiranagar", "HSR Layout", "Whitefield", "BTM Layout",
                  "Electronic City", "Hebbal", "Marathahalli", "Bannerghatta", "JP Nagar"],
    "Hyderabad": ["Banjara Hills", "Hitech City", "Madhapur", "Gachibowli", "Jubilee Hills",
                  "Kondapur", "Kukatpally", "Miyapur", "Secunderabad", "LB Nagar"],
    "Pune": ["Kothrud", "Baner", "Hinjewadi", "Wakad", "Viman Nagar",
             "Hadapsar", "Aundh", "Shivaji Nagar", "Kharadi", "Pimple Saudagar"],
    "Chennai": ["Anna Nagar", "Velachery", "Adyar", "Thoraipakkam", "Porur",
                "OMR", "Chromepet", "T Nagar", "Perambur", "Tambaram"],
    "Kolkata": ["Salt Lake", "Park Street", "Ballygunge", "Howrah", "Rajarhat",
                "Dum Dum", "Behala", "Garia", "Tollygunge", "Jadavpur"],
    "Ahmedabad": ["Satellite", "Prahlad Nagar", "Vastrapur", "Bopal", "SG Highway",
                  "Navrangpura", "Maninagar", "Chandkheda", "Gota", "Nikol"],
    "Jaipur": ["Vaishali Nagar", "Mansarovar", "Raja Park", "Malviya Nagar", "Jagatpura"],
    "Surat": ["Adajan", "Athwa", "Rander", "Katargam", "Vesu"],
}

rng = np.random.default_rng(42)


def generate_dataset(n_rows: int = 4750) -> pd.DataFrame:
    records = []
    city_list = list(CITIES.keys())
    furnishings = list(FURNISHING_MULTIPLIER.keys())

    for _ in range(n_rows):
        city = rng.choice(city_list)
        config = CITIES[city]
        bhk = int(rng.choice([1, 2, 3, 4, 5], p=[0.20, 0.42, 0.28, 0.08, 0.02]))
        size = int(rng.normal(loc=400 + bhk * 220, scale=80 + bhk * 40))
        size = max(150, min(6000, size))
        bathrooms = min(bhk, int(rng.choice([1, 2, 3, 4], p=[0.3, 0.45, 0.20, 0.05])))
        furnishing = str(rng.choice(furnishings))
        locality = str(rng.choice(AREA_LOCALITY.get(city, ["City Center"])))

        # Rent formula (realistic)
        base_rent = (
            config["base_per_sqft"] * size
            * FURNISHING_MULTIPLIER[furnishing]
            * (1 + (bhk - 1) * 0.18)
            * rng.uniform(0.80, 1.25)        # market noise
        )
        rent = max(3000, int(round(base_rent / 100) * 100))

        records.append({
            "Posted On": f"2023-{rng.integers(1, 12):02d}-{rng.integers(1, 28):02d}",
            "BHK": bhk,
            "Rent": rent,
            "Size": size,
            "Floor": f"{rng.integers(0, 15)} out of {rng.integers(15, 30)}",
            "Area Type": rng.choice(["Super Area", "Carpet Area", "Built Area"]),
            "Area Locality": locality,
            "City": city,
            "Furnishing Status": furnishing,
            "Tenant Preferred": rng.choice(["Bachelors/Family", "Family", "Bachelors"]),
            "Bathroom": bathrooms,
            "Point of Contact": rng.choice(POINT_OF_CONTACT),
        })

    df = pd.DataFrame(records)
    logger.info(f"Generated {len(df)} rows")
    logger.info(f"Rent range: ₹{df['Rent'].min():,} – ₹{df['Rent'].max():,}")
    logger.info(f"Cities: {df['City'].value_counts().to_dict()}")
    return df


if __name__ == "__main__":
    if OUTPUT_PATH.exists():
        logger.info(f"✅ Dataset already exists at {OUTPUT_PATH} — skipping generation.")
        logger.info("   Delete the file and re-run to regenerate.")
    else:
        logger.info("🏗️  Generating synthetic rental dataset…")
        df = generate_dataset(4750)
        df.to_csv(OUTPUT_PATH, index=False)
        logger.info(f"💾 Saved to {OUTPUT_PATH}")
