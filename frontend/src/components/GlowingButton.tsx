import { ReactNode } from 'react';
import { GlowingEffect } from '@/components/ui/glowing-effect';

interface GlowingButtonProps {
  children: ReactNode;
  isActive?: boolean;
  onClick: () => void;
  id?: string;
  roundedClass?: string;
  paddingClass?: string;
  activeClassName?: string;
  inactiveClassName?: string;
}

export function GlowingButton({ 
  children, 
  isActive = false, 
  onClick, 
  id,
  roundedClass = "rounded-full",
  paddingClass = "px-3 py-1.5 text-xs",
  activeClassName = "bg-violet-600 text-white shadow-lg shadow-violet-500/20",
  inactiveClassName = "bg-[#0f172a] text-gray-400 hover:text-white"
}: GlowingButtonProps) {
  return (
    <div className={`relative group p-[1px] transition-all duration-300 ${roundedClass} border border-white/5`}>
      <GlowingEffect
        spread={25}
        glow={true}
        disabled={isActive}
        proximity={48}
        inactiveZone={0.01}
      />
      <button
        id={id}
        onClick={onClick}
        className={`relative z-10 w-full h-full font-medium transition-all duration-200 ${roundedClass} ${paddingClass} ${
          isActive ? activeClassName : inactiveClassName
        }`}
      >
        {children}
      </button>
    </div>
  );
}
