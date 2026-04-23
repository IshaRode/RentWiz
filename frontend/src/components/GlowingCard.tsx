import { ReactNode } from 'react';
import { GlowingEffect } from '@/components/ui/glowing-effect';

interface GlowingCardProps {
  children: ReactNode;
  className?: string;
  wrapperClassName?: string;
}

export function GlowingCard({ children, className = '', wrapperClassName = '' }: GlowingCardProps) {
  return (
    <div className={`relative h-full rounded-2xl border border-white/5 p-[1px] transition-all duration-300 hover:shadow-xl group ${wrapperClassName}`}>
      <GlowingEffect
        spread={40}
        glow={true}
        disabled={false}
        proximity={64}
        inactiveZone={0.01}
      />
      <div className={`glass-card relative h-full overflow-hidden rounded-xl border-none ${className}`}>
        {children}
      </div>
    </div>
  );
}
