"""
RentWiz – Model Evaluation Script
Loads the trained model and reports detailed performance metrics.

Usage:
    cd backend
    python ml/evaluate.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib
import json
import numpy as np
import pandas as pd
import logging
from pathlib import Path
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent.parent / "app" / "models"
DATA_PATH = Path(__file__).parent / "data" / "house_rent.csv"


def evaluate():
    # Load artifacts
    pipeline_path = MODEL_DIR / "full_pipeline.joblib"
    if not pipeline_path.exists():
        logger.error("No trained model found. Run `python ml/train.py` first.")
        return

    pipeline = joblib.load(pipeline_path)
    logger.info(f"✅ Pipeline loaded from {pipeline_path}")

    # Load data
    df = pd.read_csv(DATA_PATH)
    col_map = {"bhk": "BHK", "size": "Size", "city": "City",
               "furnishing_status": "Furnishing Status", "bathroom": "Bathroom", "rent": "Rent"}
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    features = ["BHK", "Size", "City", "Furnishing Status", "Bathroom"]
    available = [c for c in features if c in df.columns]
    df = df[available + ["Rent"]].dropna()

    X = df[available]
    y = df["Rent"]

    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    y_pred = pipeline.predict(X_test)

    r2   = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae  = mean_absolute_error(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

    logger.info("\n" + "=" * 55)
    logger.info("📊  MODEL EVALUATION REPORT")
    logger.info("=" * 55)
    logger.info(f"  R² Score         : {r2:.4f}  {'✅ Good' if r2 > 0.75 else '⚠️  Needs tuning'}")
    logger.info(f"  RMSE             : ₹{rmse:>10,.0f}")
    logger.info(f"  MAE              : ₹{mae:>10,.0f}")
    logger.info(f"  MAPE             : {mape:.1f}%")
    logger.info("=" * 55)

    # Residual analysis
    residuals = y_test.values - y_pred
    logger.info(f"\n📐 Residual Analysis:")
    logger.info(f"  Mean residual    : ₹{residuals.mean():>8,.0f}  (bias)")
    logger.info(f"  Std  residual    : ₹{residuals.std():>8,.0f}")
    logger.info(f"  Within ±₹5000   : {(np.abs(residuals) < 5000).mean()*100:.1f}%")
    logger.info(f"  Within ±₹10000  : {(np.abs(residuals) < 10000).mean()*100:.1f}%")

    # By city
    if "City" in X_test.columns:
        logger.info(f"\n🌆 Performance by City (R²):")
        for city in X_test["City"].unique():
            mask = X_test["City"] == city
            if mask.sum() < 5:
                continue
            city_r2 = r2_score(y_test[mask], y_pred[mask])
            logger.info(f"  {city:<15} R²={city_r2:.3f}  n={mask.sum()}")

    # Load saved metrics for comparison
    metrics_path = MODEL_DIR / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            saved = json.load(f)
        logger.info(f"\n📁 Saved metrics: {saved}")


if __name__ == "__main__":
    evaluate()
