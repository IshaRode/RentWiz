'use client';
import { useState, useEffect, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { SlidersHorizontal, TrendingDown, Loader2, AlertCircle, ChevronDown } from 'lucide-react';
import DealCard from '@/components/DealCard';
import SearchForm from '@/components/SearchForm';
import { ScatterPlot } from '@/components/PriceChart';
import { getBestDeals, formatRentFull } from '@/lib/api';
import type { DealResult, SearchFilters, DealLabel } from '@/types';
import { GlowingCard } from '@/components/GlowingCard';
import { GlowingButton } from '@/components/GlowingButton';

const CITIES = ['', 'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata', 'Ahmedabad'];

function DealsContent() {
  const params = useSearchParams();
  const [deals, setDeals] = useState<DealResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    city: params.get('city') || '',
    bhk: params.get('bhk') ? Number(params.get('bhk')) : null,
    maxBudget: null,
    label: (params.get('label') as DealLabel | null) || null,
  });

  const fetchDeals = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getBestDeals({
        city: filters.city,
        bhk: filters.bhk,
        label: filters.label,
        limit: 40,
      });
      let listings = res.listings;
      if (filters.maxBudget) {
        listings = listings.filter(d => d.actual_rent <= (filters.maxBudget ?? Infinity));
      }
      setDeals(listings);
    } catch (e) {
      setError('Could not load deals. Make sure the backend is running on localhost:8000.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { fetchDeals(); }, [fetchDeals]);

  const stats = {
    total: deals.length,
    goodDeals: deals.filter(d => d.deal_label === 'good_deal').length,
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
            <TrendingDown size={16} className="text-emerald-400" />
          </div>
          <h1 className="text-3xl font-black text-white">Best Rental Deals</h1>
        </div>
        <p className="text-gray-400 ml-11">
          Properties ranked by deal score — the higher the score, the more underpriced the listing.
        </p>
      </div>

      {/* Stats strip */}
      {!loading && deals.length > 0 && (
        <div className="grid grid-cols-2 gap-4 mb-8">
          <GlowingCard className="p-4 text-center">
            <div className="text-2xl font-bold text-white">{stats.total}</div>
            <div className="text-xs text-gray-500 mt-1">Listings Found</div>
          </GlowingCard>
          <GlowingCard className="p-4 text-center">
            <div className="text-2xl font-bold text-emerald-400">{stats.goodDeals}</div>
            <div className="text-xs text-gray-500 mt-1">Great Deals</div>
          </GlowingCard>
        </div>
      )}

      {/* Filters toggle */}
      <div className="flex items-center justify-between mb-6">
        <button id="toggle-filters-btn"
          onClick={() => setShowFilters(p => !p)}
          className="btn-secondary text-sm">
          <SlidersHorizontal size={15} />
          Filters
          <ChevronDown size={14} className={`transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>
      </div>

      {/* Search form */}
      {showFilters && (
        <div className="mb-8">
          <SearchForm compact onSearch={f => setFilters(f)} />
        </div>
      )}

      {/* Quick city filter pills */}
      <div className="flex flex-wrap gap-2 mb-6">
        {CITIES.map(c => (
          <GlowingButton
            key={c || 'all'}
            id={`city-pill-${c || 'all'}`}
            onClick={() => setFilters(prev => ({ ...prev, city: c }))}
            isActive={filters.city === c}
          >
            {c || 'All Cities'}
          </GlowingButton>
        ))}
      </div>

      {/* Content */}
      {loading && (
        <div className="flex items-center justify-center py-24">
          <div className="text-center">
            <Loader2 size={36} className="text-violet-400 animate-spin mx-auto mb-4" />
            <p className="text-gray-400">Analyzing deals…</p>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/20 rounded-xl p-5 mb-6">
          <AlertCircle size={18} className="text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-400 font-medium text-sm">Backend not connected</p>
            <p className="text-gray-400 text-xs mt-1">{error}</p>
          </div>
        </div>
      )}

      {!loading && !error && deals.length === 0 && (
        <div className="text-center py-24">
          <div className="text-5xl mb-4">🔍</div>
          <p className="text-gray-400">No deals found with these filters.</p>
          <button className="btn-secondary mt-4 text-sm"
            onClick={() => setFilters({ city: '', bhk: null, maxBudget: null, label: null })}>
            Clear Filters
          </button>
        </div>
      )}

      {!loading && deals.length > 0 && (
        <>
          <div className="grid gap-5 mb-12 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {deals.map((deal, i) => (
              <DealCard key={`${deal.listing_url}-${i}`} deal={deal} rank={i + 1} />
            ))}
          </div>

          {/* Scatter Plot */}
          <GlowingCard className="p-6">
            <h2 className="text-lg font-bold text-white mb-1">
              Rent vs Area — Deal Map
            </h2>
            <p className="text-xs text-gray-500 mb-6">
              <span className="text-emerald-400">●</span> Good Deal &nbsp;
              <span className="text-yellow-400">●</span> Fair &nbsp;
              <span className="text-red-400">●</span> Overpriced
            </p>
            <ScatterPlot deals={deals} />
          </GlowingCard>
        </>
      )}
    </div>
  );
}

export default function DealsPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 size={36} className="text-violet-400 animate-spin" />
      </div>
    }>
      <DealsContent />
    </Suspense>
  );
}
