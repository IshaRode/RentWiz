'use client';
import { MapPin, Home, Maximize2, TrendingDown, TrendingUp, ExternalLink, Sparkles } from 'lucide-react';
import type { DealResult } from '@/types';
import DealBadge from './DealBadge';
import { formatRentFull } from '@/lib/api';
import { GlowingEffect } from '@/components/ui/glowing-effect';
interface DealCardProps {
  deal: DealResult;
  rank?: number;
  showExplanation?: boolean;
}

// A "real" URL is one scraped from an actual listing site, not our seeder placeholders
function isRealListingUrl(url?: string): boolean {
  if (!url) return false;
  const placeholders = ['rentwiz.app', 'example.com', '/demo-', 'demo/'];
  return !placeholders.some(p => url.includes(p));
}

export default function DealCard({ deal, rank, showExplanation = true }: DealCardProps) {
  const isGoodDeal = deal.deal_label === 'good_deal';
  const isOverpriced = deal.deal_label === 'overpriced';
  const savings = Math.abs(deal.deal_score);
  const pct = Math.abs(deal.deal_pct);
  const hasRealUrl = isRealListingUrl(deal.listing_url);

  return (
    <div className={`relative h-full rounded-2xl border p-[1px] transition-all duration-300 hover:-translate-y-1 hover:shadow-xl group
      ${isGoodDeal ? 'hover:shadow-emerald-500/10 border-emerald-500/20' : ''}
      ${isOverpriced ? 'hover:shadow-red-500/10 border-red-500/20' : 'border-white/5'}
    `}>
      <GlowingEffect
        spread={40}
        glow={true}
        disabled={false}
        proximity={64}
        inactiveZone={0.01}
      />
      <div className="glass-card relative flex flex-col h-full overflow-hidden rounded-xl p-5 border-none">
        {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div className="flex-1 min-w-0">
          {rank && (
            <span className="text-xs font-bold text-gray-500 mb-1 block">
              #{rank} Best Deal
            </span>
          )}
          <h3 className="font-semibold text-white text-sm leading-tight truncate">
            {deal.title || `${deal.bhk}BHK Apartment`}
          </h3>
          <div className="flex items-center gap-1.5 mt-1 text-gray-400 text-xs">
            <MapPin size={11} className="flex-shrink-0" />
            <span className="truncate">{deal.location || deal.city}</span>
            {deal.location && deal.location !== deal.city && (
              <span className="text-gray-600">, {deal.city}</span>
            )}
          </div>
        </div>
        <DealBadge label={deal.deal_label} />
      </div>

      {/* Property specs */}
      <div className="flex items-center gap-4 mb-4 text-gray-400 text-xs">
        <span className="flex items-center gap-1">
          <Home size={12} className="text-violet-400" />
          {deal.bhk} BHK
        </span>
        <span className="flex items-center gap-1">
          <Maximize2 size={12} className="text-cyan-400" />
          {deal.area_sqft.toLocaleString('en-IN')} sq ft
        </span>
        <span className="text-gray-600">
          {deal.furnishing.replace('-Furnished', '')}
        </span>
      </div>

      {/* Rent comparison */}
      <div className="bg-white/5 rounded-xl p-4 mb-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-xs text-gray-500 mb-1">Actual Rent</p>
            <p className="text-lg font-bold text-white">
              {formatRentFull(deal.actual_rent)}
              <span className="text-xs font-normal text-gray-400">/mo</span>
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Predicted Fair Rent</p>
            <p className={`text-lg font-bold ${isGoodDeal ? 'text-emerald-400' : isOverpriced ? 'text-red-400' : 'text-yellow-400'}`}>
              {formatRentFull(deal.predicted_rent)}
              <span className="text-xs font-normal text-gray-400">/mo</span>
            </p>
          </div>
        </div>

        {/* Deal score bar */}
        <div className="mt-3 pt-3 border-t border-white/5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              {isGoodDeal ? (
                <TrendingDown size={14} className="text-emerald-400" />
              ) : isOverpriced ? (
                <TrendingUp size={14} className="text-red-400" />
              ) : (
                <span className="text-yellow-400 text-xs">≈</span>
              )}
              <span className={`text-sm font-bold ${
                isGoodDeal ? 'text-emerald-400' : isOverpriced ? 'text-red-400' : 'text-yellow-400'
              }`}>
                {isGoodDeal ? '−' : isOverpriced ? '+' : '±'}
                {formatRentFull(savings)}/mo
              </span>
            </div>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded-md ${
              isGoodDeal ? 'bg-emerald-400/10 text-emerald-400' :
              isOverpriced ? 'bg-red-400/10 text-red-400' :
              'bg-yellow-400/10 text-yellow-400'
            }`}>
              {isGoodDeal ? `${pct}% below market` : isOverpriced ? `${pct}% above market` : 'At market rate'}
            </span>
          </div>
        </div>
      </div>

      {/* AI Explanation */}
      {showExplanation && deal.ai_explanation && (
        <div className="flex items-start gap-2 bg-violet-500/5 border border-violet-500/15 rounded-lg p-3 mb-4">
          <Sparkles size={13} className="text-violet-400 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-gray-300 leading-relaxed">{deal.ai_explanation}</p>
        </div>
      )}

      {/* Actions */}
      {hasRealUrl ? (
        <a
          href={deal.listing_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-xs font-medium
                     text-violet-400 border border-violet-500/20 hover:bg-violet-500/10 hover:border-violet-500/40
                     transition-all duration-200"
        >
          View Listing <ExternalLink size={12} />
        </a>
      ) : (
        <div className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg text-xs font-medium
                        text-gray-600 border border-white/5 cursor-default select-none">
          ML-scored listing · no external URL
        </div>
      )}
      </div>
    </div>
  );
}
