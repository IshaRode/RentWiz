'use client';
import { useState, useEffect } from 'react';
import { BarChart3, MapPin, TrendingDown, TrendingUp, Minus, Loader2, AlertCircle } from 'lucide-react';
import { getAreaInsights, formatRentFull } from '@/lib/api';
import type { AreaInsightsResponse } from '@/types';
import { RentByBHKChart, DealDistributionPie } from '@/components/PriceChart';
import SearchForm from '@/components/SearchForm';
import { GlowingCard } from '@/components/GlowingCard';
import { GlowingButton } from '@/components/GlowingButton';

const CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata', 'Ahmedabad'];

function StatCard({ label, value, sub, color = 'text-white' }: { label: string; value: string; sub?: string; color?: string }) {
  return (
    <GlowingCard className="p-5">
      <p className="text-xs text-gray-500 mb-1.5">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      {sub && <p className="text-xs text-gray-600 mt-1">{sub}</p>}
    </GlowingCard>
  );
}

export default function InsightsPage() {
  const [city, setCity] = useState('Mumbai');
  const [data, setData] = useState<AreaInsightsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInsights = async (c: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAreaInsights(c);
      setData(res);
    } catch {
      setError('Could not load insights. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchInsights(city); }, [city]);

  const dealScore = data?.avg_deal_score ?? 0;

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
            <BarChart3 size={16} className="text-cyan-400" />
          </div>
          <h1 className="text-3xl font-black text-white">Market Insights</h1>
        </div>
        <p className="text-gray-400 ml-11">
          Aggregated rental market statistics, deal distributions, and price trends by city.
        </p>
      </div>

      {/* City selector */}
      <div className="flex flex-wrap gap-2 mb-8">
        {CITIES.map(c => (
          <GlowingButton
            key={c}
            id={`insight-city-${c.toLowerCase()}`}
            onClick={() => setCity(c)}
            isActive={city === c}
            roundedClass="rounded-xl"
            paddingClass="px-4 py-2 text-sm"
            activeClassName="bg-gradient-to-r from-violet-600 to-cyan-600 text-white shadow-lg shadow-violet-500/20"
          >
            {c}
          </GlowingButton>
        ))}
      </div>

      {loading && (
        <div className="flex items-center justify-center py-32">
          <div className="text-center">
            <Loader2 size={36} className="text-violet-400 animate-spin mx-auto mb-4" />
            <p className="text-gray-400">Loading {city} insights…</p>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/20 rounded-xl p-5 mb-6">
          <AlertCircle size={18} className="text-red-400 flex-shrink-0" />
          <p className="text-gray-400 text-sm">{error}</p>
        </div>
      )}

      {!loading && data && (
        <>
          {/* City headline */}
          <div className="flex items-center gap-2 mb-6">
            <MapPin size={18} className="text-violet-400" />
            <h2 className="text-xl font-bold text-white">{data.city} Rental Market</h2>
            <span className="text-xs bg-white/5 border border-white/10 rounded-full px-2.5 py-1 text-gray-400">
              {data.total_listings} listings
            </span>
            {/* Market mood */}
            <span className={`ml-auto flex items-center gap-1.5 text-sm font-medium px-3 py-1 rounded-full
              ${dealScore > 1000 ? 'badge-good' : dealScore < -1000 ? 'badge-bad' : 'badge-fair'}`}>
              {dealScore > 1000 ? <TrendingDown size={13} /> : dealScore < -1000 ? <TrendingUp size={13} /> : <Minus size={13} />}
              {dealScore > 1000 ? 'Buyer\'s Market' : dealScore < -1000 ? 'Seller\'s Market' : 'Balanced Market'}
            </span>
          </div>

          {/* Key stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <StatCard label="Average Rent" value={formatRentFull(data.avg_rent)} sub="/month" />
            <StatCard label="Median Rent" value={formatRentFull(data.median_rent)} sub="/month" color="text-cyan-400" />
            <StatCard label="Lowest Rent" value={formatRentFull(data.min_rent)} sub="/month" color="text-emerald-400" />
            <StatCard label="Highest Rent" value={formatRentFull(data.max_rent)} sub="/month" color="text-red-400" />
          </div>

          {/* Charts row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Avg Rent by BHK */}
            <GlowingCard className="p-6">
              <h3 className="text-base font-bold text-white mb-1">Average Rent by BHK</h3>
              <p className="text-xs text-gray-500 mb-5">How bedroom count drives rent in {city}</p>
              <RentByBHKChart data={data.rent_by_bhk} />
            </GlowingCard>

            {/* Deal distribution pie */}
            <GlowingCard className="p-6">
              <h3 className="text-base font-bold text-white mb-1">Deal Distribution</h3>
              <p className="text-xs text-gray-500 mb-5">What proportion of listings are good deals</p>
              <DealDistributionPie distribution={data.deal_distribution} />
            </GlowingCard>
          </div>

          {/* Top localities */}
          <GlowingCard className="p-6" wrapperClassName="mb-8">
            <h3 className="text-base font-bold text-white mb-5">Top Localities by Average Rent</h3>
            <div className="space-y-3">
              {data.top_localities.map((loc, i) => {
                const pct = (loc.avg_rent / data.max_rent) * 100;
                return (
                  <div key={loc.location} className="flex items-center gap-4">
                    <span className="text-xs text-gray-500 w-5 text-right">{i + 1}</span>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-sm text-white font-medium">{loc.location}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-gray-500">{loc.listings} listings</span>
                          <span className="text-sm font-semibold text-cyan-400">{formatRentFull(loc.avg_rent)}/mo</span>
                        </div>
                      </div>
                      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-violet-600 to-cyan-500 rounded-full transition-all duration-700"
                          style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </GlowingCard>

          {/* Deal summary cards */}
          <div className="grid grid-cols-3 gap-4">
            <GlowingCard className="p-5 border-emerald-500/20">
              <div className="text-3xl font-black text-emerald-400">{data.deal_distribution.good_deal}</div>
              <div className="text-sm text-white font-medium mt-1">Great Deals</div>
              <div className="text-xs text-gray-500 mt-1">Priced below market</div>
            </GlowingCard>
            <GlowingCard className="p-5 border-yellow-500/20">
              <div className="text-3xl font-black text-yellow-400">{data.deal_distribution.fair}</div>
              <div className="text-sm text-white font-medium mt-1">Fair Price</div>
              <div className="text-xs text-gray-500 mt-1">Within market range</div>
            </GlowingCard>
            <GlowingCard className="p-5 border-red-500/20">
              <div className="text-3xl font-black text-red-400">{data.deal_distribution.overpriced}</div>
              <div className="text-sm text-white font-medium mt-1">Overpriced</div>
              <div className="text-xs text-gray-500 mt-1">Above market rate</div>
            </GlowingCard>
          </div>
        </>
      )}
    </div>
  );
}
