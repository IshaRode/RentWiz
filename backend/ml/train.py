"""
RentWiz – ML Training Pipeline
Trains a GradientBoostingRegressor to predict rental prices
from the Kaggle House_Rent_Dataset.csv.

Usage:
    cd backend
    python ml/train.py

Outputs:
    app/models/rent_model.joblib
    app/models/preprocessor.joblib
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

# ─── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "house_rent.csv"
MODEL_DIR = Path(__file__).parent.parent / "app" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ─── Feature config ─────────────────────────────────────────────────────────────
NUMERIC_FEATURES = ["BHK", "Size", "Bathroom"]
CATEGORICAL_FEATURES = ["City", "Furnishing Status"]
TARGET = "Rent"


def load_and_clean_data(path: Path) -> pd.DataFrame:
    logger.info(f"📂 Loading data from {path}")
    df = pd.read_csv(path)
    logger.info(f"   Raw shape: {df.shape}")

    # Rename columns to expected names if needed
    col_map = {
        "bhk": "BHK", "size": "Size", "city": "City",
        "furnishing_status": "Furnishing Status",
        "bathroom": "Bathroom", "rent": "Rent",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # Select only needed columns
    needed = NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET]
    available = [c for c in needed if c in df.columns]
    df = df[available].copy()

    # Fill missing categoricals
    for col in ["Furnishing Status"]:
        if col in df.columns:
            df[col] = df[col].fillna("Semi-Furnished")

    # Drop rows with missing target or key features
    df = df.dropna(subset=[TARGET, "BHK", "Size"])

    # Remove outliers (rent > 99th percentile or < 1st percentile)
    q_low = df[TARGET].quantile(0.01)
    q_high = df[TARGET].quantile(0.99)
    df = df[(df[TARGET] >= q_low) & (df[TARGET] <= q_high)]

    # Clamp size to reasonable range
    df = df[(df["Size"] >= 100) & (df["Size"] <= 10000)]

    logger.info(f"   Clean shape: {df.shape}")
    return df


def build_pipeline() -> Pipeline:
    """Build sklearn preprocessing + model pipeline."""
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    model = GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.08,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        subsample=0.85,
        random_state=42,
    )

    return Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ])


def train():
    df = load_and_clean_data(DATA_PATH)

    # Handle missing categorical features by adding defaults
    for col in CATEGORICAL_FEATURES:
        if col not in df.columns:
            logger.warning(f"Column '{col}' missing, adding default")
            df[col] = "Unknown"
    for col in NUMERIC_FEATURES:
        if col not in df.columns:
            df[col] = 1

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    logger.info(f"📊 Train: {len(X_train)} | Test: {len(X_test)}")

    pipeline = build_pipeline()
    logger.info("🏋️  Training GradientBoostingRegressor…")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)

    logger.info("=" * 50)
    logger.info(f"✅ R²   Score : {r2:.4f}")
    logger.info(f"✅ RMSE       : ₹{rmse:,.0f}")
    logger.info(f"✅ MAE        : ₹{mae:,.0f}")
    logger.info("=" * 50)

    # Cross-validation
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring="r2")
    logger.info(f"📈 5-Fold CV R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Feature importance (from the GBR model layer)
    gbr = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["preprocessor"]
    try:
        feature_names = (
            NUMERIC_FEATURES
            + list(preprocessor.named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES))
        )
        importances = gbr.feature_importances_
        feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        logger.info("\n📌 Top 10 Feature Importances:")
        for name, imp in feat_imp[:10]:
            bar = "█" * int(imp * 50)
            logger.info(f"   {name:<35} {imp:.4f} {bar}")
    except Exception as e:
        logger.warning(f"Could not extract feature importances: {e}")

    # Save full pipeline (preprocessor is embedded)
    # Save separate preprocessor for the prediction service interface
    model_path = MODEL_DIR / "rent_model.joblib"
    preprocessor_path = MODEL_DIR / "preprocessor.joblib"

    joblib.dump(pipeline.named_steps["model"], model_path)
    joblib.dump(pipeline.named_steps["preprocessor"], preprocessor_path)

    # Also save the full pipeline for convenience
    joblib.dump(pipeline, MODEL_DIR / "full_pipeline.joblib")

    logger.info(f"\n💾 Model saved     → {model_path}")
    logger.info(f"💾 Preprocessor    → {preprocessor_path}")
    logger.info(f"💾 Full pipeline   → {MODEL_DIR / 'full_pipeline.joblib'}")

    # Save metrics to file
    metrics = {
        "r2": round(r2, 4),
        "rmse": round(rmse, 2),
        "mae": round(mae, 2),
        "cv_r2_mean": round(cv_scores.mean(), 4),
        "cv_r2_std": round(cv_scores.std(), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }
    import json
    with open(MODEL_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"📊 Metrics saved   → {MODEL_DIR / 'metrics.json'}")

    return pipeline, metrics


if __name__ == "__main__":
    train()
