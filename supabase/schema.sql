-- ============================================================
-- RentWiz – Supabase PostgreSQL Schema
-- Run this in your Supabase SQL editor
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------
-- 1. Training data reference (loaded from Kaggle CSV)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS rent_training_data (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    city          TEXT        NOT NULL,
    bhk           INTEGER     NOT NULL,
    size_sqft     INTEGER     NOT NULL,
    furnishing    TEXT        NOT NULL DEFAULT 'Semi-Furnished',
    bathrooms     INTEGER     NOT NULL DEFAULT 1,
    rent          INTEGER     NOT NULL,
    source        TEXT        DEFAULT 'kaggle',
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- ------------------------------------------------------------
-- 2. Live scraped listings (from Selenium scraper)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS scraped_listings (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title            TEXT,
    location         TEXT        NOT NULL,
    city             TEXT        NOT NULL,
    bhk              INTEGER,
    area_sqft        INTEGER,
    furnishing       TEXT        DEFAULT 'Semi-Furnished',
    bathrooms        INTEGER     DEFAULT 1,
    actual_rent      INTEGER     NOT NULL,
    predicted_rent   INTEGER,
    deal_score       INTEGER     GENERATED ALWAYS AS (predicted_rent - actual_rent) STORED,
    deal_label       TEXT        CHECK (deal_label IN ('good_deal', 'fair', 'overpriced')),
    deal_pct         NUMERIC(6,2),   -- % underpriced (negative = overpriced)
    ai_explanation   TEXT,
    listing_url      TEXT        UNIQUE,
    url_hash         TEXT        UNIQUE,  -- MD5 of URL for fast dedup
    scraped_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);

-- ------------------------------------------------------------
-- 3. Area market insights (precomputed cache)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS area_insights (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    city             TEXT        NOT NULL UNIQUE,
    avg_rent         INTEGER,
    median_rent      INTEGER,
    min_rent         INTEGER,
    max_rent         INTEGER,
    total_listings   INTEGER     DEFAULT 0,
    good_deals_count INTEGER     DEFAULT 0,
    fair_count       INTEGER     DEFAULT 0,
    overpriced_count INTEGER     DEFAULT 0,
    last_updated     TIMESTAMPTZ DEFAULT now()
);

-- ------------------------------------------------------------
-- Indexes for performance
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_listings_city         ON scraped_listings(city);
CREATE INDEX IF NOT EXISTS idx_listings_deal_score   ON scraped_listings(deal_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_listings_deal_label   ON scraped_listings(deal_label);
CREATE INDEX IF NOT EXISTS idx_listings_bhk          ON scraped_listings(bhk);
CREATE INDEX IF NOT EXISTS idx_listings_scraped_at   ON scraped_listings(scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_training_city         ON rent_training_data(city);

-- ------------------------------------------------------------
-- Auto-update updated_at trigger
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_listings_updated_at
    BEFORE UPDATE ON scraped_listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------------------------------------
-- Row Level Security (enable, public read for demo)
-- ------------------------------------------------------------
ALTER TABLE scraped_listings    ENABLE ROW LEVEL SECURITY;
ALTER TABLE rent_training_data  ENABLE ROW LEVEL SECURITY;
ALTER TABLE area_insights       ENABLE ROW LEVEL SECURITY;

-- Public read access (anon key)
CREATE POLICY "Public read scraped_listings"
    ON scraped_listings FOR SELECT USING (true);

CREATE POLICY "Public read area_insights"
    ON area_insights FOR SELECT USING (true);

-- Service role full access (used by FastAPI backend)
CREATE POLICY "Service role full access listings"
    ON scraped_listings FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access training"
    ON rent_training_data FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access insights"
    ON area_insights FOR ALL USING (auth.role() = 'service_role');
