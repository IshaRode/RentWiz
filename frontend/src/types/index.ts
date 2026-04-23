// RentWiz – TypeScript type definitions

export type DealLabel = 'good_deal' | 'fair' | 'overpriced';

export interface PropertyFeatures {
  city: string;
  bhk: number;
  area_sqft: number;
  furnishing: 'Furnished' | 'Semi-Furnished' | 'Unfurnished';
  bathrooms: number;
}

export interface PropertyWithRent extends PropertyFeatures {
  actual_rent: number;
  listing_url?: string;
  title?: string;
  location?: string;
}

export interface PredictResponse {
  predicted_rent: number;
  city: string;
  bhk: number;
  area_sqft: number;
  furnishing: string;
  bathrooms: number;
  confidence_note: string;
}

export interface DealResult {
  title?: string;
  location?: string;
  city: string;
  bhk: number;
  area_sqft: number;
  furnishing: string;
  bathrooms: number;
  actual_rent: number;
  predicted_rent: number;
  deal_score: number;
  deal_pct: number;
  deal_label: DealLabel;
  deal_label_display: string;
  ai_explanation?: string;
  listing_url?: string;
  scraped_at?: string;
}

export interface BestDealsResponse {
  listings: DealResult[];
  total: number;
  filters_applied: Record<string, unknown>;
}

export interface AreaInsightsResponse {
  city: string;
  avg_rent: number;
  median_rent: number;
  min_rent: number;
  max_rent: number;
  total_listings: number;
  deal_distribution: { good_deal: number; fair: number; overpriced: number };
  avg_deal_score: number;
  top_localities: { location: string; avg_rent: number; listings: number }[];
  rent_by_bhk: { bhk: number; avg_rent: number; count: number }[];
}

export interface SearchFilters {
  city: string;
  bhk: number | null;
  maxBudget: number | null;
  label: DealLabel | null;
}
