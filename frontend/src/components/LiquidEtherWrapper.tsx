"use client";

import dynamic from 'next/dynamic';

const LiquidEther = dynamic(() => import('./LiquidEther'), { ssr: false });

export default function LiquidEtherWrapper() {
  return (
    <div className="fixed inset-0 w-full h-full pointer-events-none opacity-80 mix-blend-screen">
      <LiquidEther
        colors={['#5227FF', '#FF9FFC', '#B497CF']}
        mouseForce={20}
        cursorSize={100}
        isViscous={true}
        viscous={30}
        iterationsViscous={32}
        iterationsPoisson={32}
        resolution={0.5}
        isBounce={false}
        autoDemo={true}
        autoSpeed={0.5}
        autoIntensity={2.2}
        takeoverDuration={0.25}
        autoResumeDelay={3000}
        autoRampDuration={0.6}
      />
    </div>
  );
}
