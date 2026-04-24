'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search, MapPin, Home, Maximize2, IndianRupee, Zap } from 'lucide-react';
import type { SearchFilters } from '@/types';
import { GlowingCard } from '@/components/GlowingCard';

const CITIES = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata', 'Ahmedabad'];
const BHK_OPTIONS = [1, 2, 3, 4];

interface SearchFormProps {
  onSearch?: (filters: SearchFilters) => void;
  compact?: boolean;
}

export default function SearchForm({ onSearch, compact = false }: SearchFormProps) {
  const router = useRouter();
  const [filters, setFilters] = useState<SearchFilters>({
    city: 'Mumbai',
    bhk: 2,
    maxBudget: null,
    label: null,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(filters);
    } else {
      const params = new URLSearchParams();
      if (filters.city) params.set('city', filters.city);
      if (filters.bhk) params.set('bhk', String(filters.bhk));
      if (filters.label) params.set('label', filters.label);
      router.push(`/deals?${params.toString()}`);
    }
  };

  const set = (key: keyof SearchFilters, value: unknown) =>
    setFilters(prev => ({ ...prev, [key]: value }));

  if (compact) {
    return (
      <form onSubmit={handleSubmit} className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-[140px]">
          <label className="block text-xs text-gray-400 mb-1.5 font-medium">City</label>
          <select id="city-select-compact" className="select-field text-sm py-2.5"
            value={filters.city} onChange={e => set('city', e.target.value)}>
            <option value="">All Cities</option>
            {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="w-24">
          <label className="block text-xs text-gray-400 mb-1.5 font-medium">BHK</label>
          <select id="bhk-select-compact" className="select-field text-sm py-2.5"
            value={filters.bhk ?? ''} onChange={e => set('bhk', e.target.value ? Number(e.target.value) : null)}>
            <option value="">Any</option>
            {BHK_OPTIONS.map(b => <option key={b} value={b}>{b}BHK</option>)}
          </select>
        </div>
        <div className="flex-1 min-w-[130px]">
          <label className="block text-xs text-gray-400 mb-1.5 font-medium">Deal Type</label>
          <select id="deal-filter-compact" className="select-field text-sm py-2.5"
            value={filters.label ?? ''} onChange={e => set('label', e.target.value || null)}>
            <option value="">All Deals</option>
            <option value="good_deal">🟢 Good</option>
            <option value="fair">🟡 Fair</option>
            <option value="overpriced">🔴 Overpriced</option>
          </select>
        </div>
        <button id="search-btn-compact" type="submit" className="btn-primary py-2.5 px-5 text-sm">
          <Search size={14} /> Search
        </button>
      </form>
    );
  }

  return (
    <GlowingCard className="p-6 md:p-8 glow-violet">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* City */}
        <div className="lg:col-span-1">
          <label htmlFor="city-select" className="block text-sm text-gray-400 mb-2 font-medium flex items-center gap-1.5">
            <MapPin size={14} className="text-violet-400" /> City
          </label>
          <select id="city-select" className="select-field"
            value={filters.city} onChange={e => set('city', e.target.value)}>
            <option value="">All Cities</option>
            {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        {/* BHK */}
        <div>
          <label htmlFor="bhk-select" className="block text-sm text-gray-400 mb-2 font-medium flex items-center gap-1.5">
            <Home size={14} className="text-cyan-400" /> BHK Type
          </label>
          <select id="bhk-select" className="select-field"
            value={filters.bhk ?? ''} onChange={e => set('bhk', e.target.value ? Number(e.target.value) : null)}>
            <option value="">Any BHK</option>
            {BHK_OPTIONS.map(b => <option key={b} value={b}>{b} BHK</option>)}
          </select>
        </div>

        {/* Max Budget */}
        <div>
          <label htmlFor="budget-input" className="block text-sm text-gray-400 mb-2 font-medium flex items-center gap-1.5">
            <IndianRupee size={14} className="text-emerald-400" /> Max Budget (₹/mo)
          </label>
          <input id="budget-input" type="number" placeholder="e.g. 35000" className="input-field"
            min={1000} max={500000} step={1000}
            value={filters.maxBudget ?? ''}
            onChange={e => set('maxBudget', e.target.value ? Number(e.target.value) : null)} />
        </div>

        {/* Deal Filter */}
        <div>
          <label htmlFor="deal-filter" className="block text-sm text-gray-400 mb-2 font-medium flex items-center gap-1.5">
            <Zap size={14} className="text-yellow-400" /> Deal Type
          </label>
          <select id="deal-filter" className="select-field"
            value={filters.label ?? ''} onChange={e => set('label', e.target.value || null)}>
            <option value="">All Deals</option>
            <option value="good_deal">🟢 Good Deals Only</option>
            <option value="fair">🟡 Fair Price</option>
            <option value="overpriced">🔴 Overpriced</option>
          </select>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <button id="find-deals-btn" type="submit" className="btn-primary flex-1 py-3.5">
          <Search size={18} />
          Find Best Deals
        </button>
        <button id="reset-filters-btn" type="button" className="btn-secondary"
          onClick={() => setFilters({ city: 'Mumbai', bhk: 2, maxBudget: null, label: null })}>
          Reset Filters
        </button>
        </div>
      </form>
    </GlowingCard>
  );
}
