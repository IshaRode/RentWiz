-- Migration: Add source column to scraped_listings
-- Run this in your Supabase SQL Editor

ALTER TABLE scraped_listings 
ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'seeded';

-- Mark existing data as seeded
UPDATE scraped_listings SET source = 'seeded' WHERE source IS NULL;

-- Add index for fast source filtering
CREATE INDEX IF NOT EXISTS idx_listings_source ON scraped_listings(source);

-- Verify
SELECT source, COUNT(*) FROM scraped_listings GROUP BY source;

