// RentWiz – Typed API client
import axios from 'axios';
import type {
  PropertyFeatures,
  PropertyWithRent,
  PredictResponse,
  DealResult,
  BestDealsResponse,
  AreaInsightsResponse,
  DealLabel,
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

export async function predictRent(features: PropertyFeatures): Promise<PredictResponse> {
  const { data } = await api.post<PredictResponse>('/predict', features);
  return data;
}

export async function analyzeProperty(prop: PropertyWithRent): Promise<DealResult> {
  const { data } = await api.post<DealResult>('/analyze', prop);
  return data;
}

export async function getBestDeals(params: {
  city?: string;
  bhk?: number | null;
  label?: DealLabel | null;
  limit?: number;
  offset?: number;
}): Promise<BestDealsResponse> {
  const query = new URLSearchParams();
  if (params.city) query.set('city', params.city);
  if (params.bhk) query.set('bhk', String(params.bhk));
  if (params.label) query.set('label', params.label);
  if (params.limit) query.set('limit', String(params.limit));
  if (params.offset) query.set('offset', String(params.offset));
  const { data } = await api.get<BestDealsResponse>(`/best-deals?${query.toString()}`);
  return data;
}

export async function getAreaInsights(city: string): Promise<AreaInsightsResponse> {
  const { data } = await api.get<AreaInsightsResponse>(`/area-insights?city=${encodeURIComponent(city)}`);
  return data;
}

export function formatRent(amount: number): string {
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`;
  return `₹${amount}`;
}

export function formatRentFull(amount: number): string {
  return `₹${amount.toLocaleString('en-IN')}`;
}
