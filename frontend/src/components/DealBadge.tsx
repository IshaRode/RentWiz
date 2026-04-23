'use client';
import type { DealLabel } from '@/types';

interface DealBadgeProps {
  label: DealLabel;
  display?: string;
  size?: 'sm' | 'md';
}

const CONFIG: Record<DealLabel, { className: string; emoji: string; text: string }> = {
  good_deal:  { className: 'badge-good',  emoji: '🟢', text: 'Great Deal'  },
  fair:       { className: 'badge-fair',  emoji: '🟡', text: 'Fair Price'  },
  overpriced: { className: 'badge-bad',   emoji: '🔴', text: 'Overpriced'  },
};

export default function DealBadge({ label, display, size = 'md' }: DealBadgeProps) {
  const { className, emoji, text } = CONFIG[label] ?? CONFIG.fair;
  const sizeClass = size === 'sm'
    ? 'text-xs px-2 py-0.5 rounded-md'
    : 'text-sm px-3 py-1 rounded-lg';
  return (
    <span className={`inline-flex items-center gap-1.5 font-semibold ${className} ${sizeClass}`}>
      {emoji} {display ?? text}
    </span>
  );
}
