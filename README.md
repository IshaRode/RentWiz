# 🏠 RentWiz – AI-Powered Rental Deal Finder

> Discover rental properties priced **below fair market value** using machine learning — not just cheap listings, but genuine deals backed by data.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange)](https://scikit-learn.org)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green)](https://supabase.com)

---

## 🎯 What is RentWiz?

RentWiz identifies **underpriced rental properties** by:
1. Training a ML regression model on 4,700+ Indian rental listings
2. Predicting the **fair market rent** for any property
3. Scoring each live listing: `deal_score = predicted_rent − actual_rent`
4. Ranking all properties by deal score (positive = underpriced = good deal)
5. Generating AI explanations for each deal via Gemini

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Next.js Frontend                      │
│     Landing  │  Best Deals  │  Market Insights            │
│  (Port 3000) │  (Recharts)  │  (Recharts Charts)          │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (axios)
┌────────────────────────▼────────────────────────────────┐
│                    FastAPI Backend                        │
│  POST /predict  │  POST /analyze  │  GET /best-deals      │
│  GET /area-insights              (Port 8000)              │
└──────────┬─────────────────────────────┬────────────────┘
           │                             │
┌──────────▼──────────┐    ┌────────────▼────────────────┐
│   scikit-learn ML   │    │      Supabase (PostgreSQL)   │
│  GradientBoosting   │    │  scraped_listings            │
│  rent_model.joblib  │    │  rent_training_data          │
└─────────────────────┘    └──────────────────────────────┘
                                         ▲
                           ┌─────────────┴───────────────┐
                           │   Selenium Scraper           │
                           │  MagicBricks → Supabase      │
                           │  APScheduler (every 6h)      │
                           └──────────────────────────────┘
```

---

## 📁 Project Structure

```
RentWiz/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── api/v1/
│   │   │   ├── predict.py           # POST /predict
│   │   │   ├── analyze.py           # POST /analyze
│   │   │   ├── deals.py             # GET /best-deals
│   │   │   └── insights.py          # GET /area-insights
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic Settings
│   │   │   └── database.py          # Supabase client
│   │   ├── schemas/
│   │   │   ├── property.py
│   │   │   └── deal.py
│   │   ├── services/
│   │   │   ├── prediction.py        # ML inference
│   │   │   ├── deal_scorer.py       # Scoring algorithm
│   │   │   └── ai_explainer.py      # Gemini AI
│   │   └── models/                  # .joblib artifacts
│   ├── ml/
│   │   ├── train.py                 # Model training
│   │   ├── evaluate.py              # Performance report
│   │   ├── generate_dataset.py      # Synthetic data
│   │   └── data/
│   │       └── house_rent.csv       # Training data
│   ├── scraper/
│   │   ├── magicbricks_scraper.py   # Selenium scraper
│   │   └── scheduler.py             # APScheduler
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx           # Root layout + nav
│   │   │   ├── page.tsx             # Landing page
│   │   │   ├── deals/page.tsx       # Best deals
│   │   │   └── insights/page.tsx    # Market insights
│   │   ├── components/
│   │   │   ├── SearchForm.tsx
│   │   │   ├── DealCard.tsx
│   │   │   ├── DealBadge.tsx
│   │   │   ├── PriceChart.tsx       # Recharts wrappers
│   │   │   └── AIExplanation.tsx
│   │   ├── lib/api.ts               # Typed API client
│   │   └── types/index.ts
│   ├── next.config.ts
│   └── package.json
│
├── supabase/
│   └── schema.sql                   # Full DB schema
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Chrome browser (for Selenium scraper)
- Supabase account (optional — app works with demo data)

---

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd RentWiz
```

---

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your Supabase credentials (optional)
```

#### Train the ML Model

```bash
# Step 1: Generate training dataset (or place real Kaggle CSV at ml/data/house_rent.csv)
python ml/generate_dataset.py

# Step 2: Train the model
python ml/train.py
# Output: R², RMSE, MAE metrics + saves model artifacts

# Step 3 (optional): Detailed evaluation report
python ml/evaluate.py
```

**Expected Model Performance:**
| Metric | Value |
|--------|-------|
| R² Score | 0.83 – 0.87 |
| RMSE | ₹4,200 – ₹5,800 |
| MAE | ₹2,800 – ₹4,000 |
| 5-Fold CV R² | 0.81 ± 0.03 |

#### Start the API

```bash
# From backend/ directory
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.example .env.local
# Edit .env.local with your API URL (default: http://localhost:8000/api/v1)

# Start dev server
npm run dev
```

Frontend: http://localhost:3000

---

### 4. Database Setup (Optional)

If you want live scraped data instead of demo data:

1. Create a [Supabase](https://supabase.com) project
2. Run `supabase/schema.sql` in the Supabase SQL editor
3. Add your credentials to `backend/.env`
4. Run the scraper:

```bash
cd backend
python scraper/magicbricks_scraper.py --city Mumbai --bhk 2 --max 30 --save
```

Or start the automated scheduler:

```bash
python scraper/scheduler.py
# Runs every 6 hours across 8 target city/BHK combos
```

---

## 🔌 API Reference

### `POST /api/v1/predict`
Predict fair market rent for a property.

```json
// Request
{ "city": "Mumbai", "bhk": 2, "area_sqft": 900, "furnishing": "Semi-Furnished", "bathrooms": 2 }

// Response
{ "predicted_rent": 32400, "city": "Mumbai", "bhk": 2, "area_sqft": 900, ... }
```

### `POST /api/v1/analyze`
Full deal analysis with score and AI explanation.

```json
// Request
{ "city": "Mumbai", "bhk": 2, "area_sqft": 900, "actual_rent": 25000, "furnishing": "Semi-Furnished", "bathrooms": 2 }

// Response
{
  "predicted_rent": 32400,
  "deal_score": 7400,          // positive = underpriced
  "deal_pct": 22.8,            // 22.8% below market
  "deal_label": "good_deal",
  "ai_explanation": "This 2BHK is priced ₹7,400/month below the fair market rate — a 22.8% saving vs comparable properties."
}
```

### `GET /api/v1/best-deals`
Returns top-ranked listings sorted by deal score.

```
GET /api/v1/best-deals?city=Mumbai&bhk=2&label=good_deal&limit=20
```

### `GET /api/v1/area-insights`
City-level market statistics.

```
GET /api/v1/area-insights?city=Bangalore
```

---

## 🧠 Deal Scoring Algorithm

```
deal_score = predicted_rent − actual_rent

deal_label:
  deal_score > ₹2,000  →  "good_deal"   🟢
  deal_score < −₹2,000 →  "overpriced"  🔴
  otherwise            →  "fair"         🟡
```

The thresholds are configurable via environment variables:
- `GOOD_DEAL_THRESHOLD` (default: 2000)
- `OVERPRICED_THRESHOLD` (default: -2000)

---

## 🤖 ML Model

**Algorithm:** GradientBoostingRegressor (scikit-learn)  
**Features:**
| Feature | Type |
|---------|------|
| BHK | Numeric |
| Size (sq ft) | Numeric |
| Bathrooms | Numeric |
| City | Categorical (OneHotEncoded) |
| Furnishing Status | Categorical (OneHotEncoded) |

**Pipeline:**
```
ColumnTransformer → GradientBoostingRegressor
(StandardScaler for numeric, OneHotEncoder for categorical)
```

To use a custom Kaggle dataset, download [`House_Rent_Dataset.csv`](https://www.kaggle.com/datasets/iamsouravbanerjee/house-rent-prediction-dataset) and place it at `backend/ml/data/house_rent.csv`.

---

## 🌐 Optional: Gemini AI Explanations

Add your Google Gemini API key to `backend/.env`:
```env
GEMINI_API_KEY=your-key-here
USE_AI_EXPLANATIONS=true
```

The system gracefully falls back to template-based explanations if the key is not set.

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## 🚢 Deployment

| Component | Platform |
|-----------|----------|
| Frontend | Vercel (push to `main`) |
| Backend | Render / Fly.io / Railway |
| Database | Supabase Cloud |

**Vercel:** Set `NEXT_PUBLIC_API_URL` to your production backend URL.  
**Render:** Deploy `backend/` with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

---

## 📊 Screenshots

| Page | Description |
|------|-------------|
| `/` | Landing page with search form |
| `/deals` | Deal cards ranked by score + scatter chart |
| `/insights` | City stats, BHK chart, deal distribution pie |

---

## 📝 Design Principles

1. **Data quality > feature breadth** — model accuracy is the core value
2. **Transparent scoring** — every deal score is explainable
3. **Graceful degradation** — demo data when Supabase/scraper unavailable
4. **Modular architecture** — swap ML model, scraper, or DB independently

---

