'use client';
import { useState } from 'react';
import { TrendingDown, Sparkles, BarChart3, Search, ArrowRight, Star, Shield, Zap } from 'lucide-react';
import Link from 'next/link';
import SearchForm from '@/components/SearchForm';

const STATS = [
  { label: 'Listings Analyzed', value: '4,700+', icon: BarChart3, color: 'text-violet-400' },
  { label: 'Cities Covered', value: '10', icon: Search, color: 'text-cyan-400' },
  { label: 'Avg Savings Found', value: '₹4,200/mo', icon: TrendingDown, color: 'text-emerald-400' },
  { label: 'ML Accuracy (R²)', value: '0.85+', icon: Sparkles, color: 'text-yellow-400' },
];

const FEATURES = [
  {
    icon: Sparkles,
    title: 'AI-Powered Predictions',
    description: 'GradientBoosting ML model trained on 4,700+ Indian rental listings to predict fair market rent.',
    color: 'from-violet-500/20 to-violet-600/5',
    border: 'border-violet-500/20',
    iconBg: 'bg-violet-500/20',
    iconColor: 'text-violet-400',
  },
  {
    icon: TrendingDown,
    title: 'Deal Score Algorithm',
    description: 'Transparent scoring: Deal Score = Predicted Rent − Actual Rent. Positive means you save money.',
    color: 'from-emerald-500/20 to-emerald-600/5',
    border: 'border-emerald-500/20',
    iconBg: 'bg-emerald-500/20',
    iconColor: 'text-emerald-400',
  },
  {
    icon: BarChart3,
    title: 'Market Insights',
    description: 'Explore rent distributions, BHK breakdowns, and price trends across India\'s top cities.',
    color: 'from-cyan-500/20 to-cyan-600/5',
    border: 'border-cyan-500/20',
    iconBg: 'bg-cyan-500/20',
    iconColor: 'text-cyan-400',
  },
  {
    icon: Shield,
    title: 'Transparent & Explainable',
    description: 'Every deal score is backed by AI explanations so you always understand why a property is underpriced.',
    color: 'from-yellow-500/20 to-yellow-600/5',
    border: 'border-yellow-500/20',
    iconBg: 'bg-yellow-500/20',
    iconColor: 'text-yellow-400',
  },
];

const HOW_IT_WORKS = [
  { step: '01', title: 'Set Your Criteria', desc: 'Choose city, BHK type, and budget range.' },
  { step: '02', title: 'ML Predicts Fair Rent', desc: 'Our model calculates what the property should cost based on comparables.' },
  { step: '03', title: 'Compare & Score', desc: 'Deal Score = Predicted − Actual. Higher score = better deal.' },
  { step: '04', title: 'AI Explains the Deal', desc: 'Get a plain-English explanation of why each property is a good or bad deal.' },
];

export default function HomePage() {
  const [heroVisible] = useState(true);

  return (
    <div className="min-h-screen">
      {/* ── Hero ──────────────────────────────────────────────── */}
      <section className="relative overflow-hidden pt-20 pb-32 px-6">
        {/* Background glows */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-600/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-20 right-1/4 w-80 h-80 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent" />

        <div className="max-w-5xl mx-auto text-center relative">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-violet-500/10 border border-violet-500/25 rounded-full px-4 py-1.5 text-sm text-violet-300 mb-8 animate-fade-in-up">
            <Sparkles size={13} />
            AI-Powered Rental Intelligence
            <Zap size={13} />
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-black leading-tight mb-6 animate-fade-in-up delay-100">
            Find Rentals{' '}
            <span className="gradient-text">Priced Below</span>
            <br />Market Value
          </h1>

          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 animate-fade-in-up delay-200 leading-relaxed">
            RentWiz uses machine learning to predict fair market rent and identifies listings
            that are genuinely underpriced — not just cheap. Save thousands every month.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fade-in-up delay-300">
            <Link href="/deals" id="hero-find-deals-btn" className="btn-primary text-base px-8 py-4">
              Find Best Deals Now <ArrowRight size={18} />
            </Link>
            <Link href="/insights" id="hero-insights-btn" className="btn-secondary text-base px-8 py-4">
              <BarChart3 size={18} /> Market Insights
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-fade-in-up delay-300">
            {STATS.map((stat) => (
              <div key={stat.label} className="glass-card p-4 text-center">
                <stat.icon size={20} className={`${stat.color} mx-auto mb-2`} />
                <div className="text-2xl font-bold text-white">{stat.value}</div>
                <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Search Section ────────────────────────────────────── */}
      <section className="max-w-4xl mx-auto px-6 -mt-8 relative z-10 mb-20">
        <div className="mb-4">
          <h2 className="text-xl font-bold text-white mb-1">Search Rental Deals</h2>
          <p className="text-sm text-gray-400">Find underpriced properties in your preferred city</p>
        </div>
        <SearchForm />
      </section>

      {/* ── Features ─────────────────────────────────────────── */}
      <section className="max-w-7xl mx-auto px-6 mb-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-black text-white mb-3">
            Why <span className="gradient-text">RentWiz</span>?
          </h2>
          <p className="text-gray-400 max-w-xl mx-auto">
            Built for renters who deserve data-driven insights, not just listings.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {FEATURES.map((f) => (
            <div key={f.title}
              className={`relative rounded-2xl bg-gradient-to-br ${f.color} border ${f.border} p-6 hover:scale-[1.01] transition-transform duration-200`}>
              <div className={`w-10 h-10 rounded-xl ${f.iconBg} flex items-center justify-center mb-4`}>
                <f.icon size={20} className={f.iconColor} />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">{f.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────────── */}
      <section className="max-w-5xl mx-auto px-6 mb-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-black text-white mb-3">How It Works</h2>
          <p className="text-gray-400">Four simple steps to finding your next great deal</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {HOW_IT_WORKS.map((step, i) => (
            <div key={step.step} className="relative">
              {i < HOW_IT_WORKS.length - 1 && (
                <div className="hidden lg:block absolute top-6 left-[calc(100%+0px)] w-full h-px bg-gradient-to-r from-violet-500/30 to-transparent z-10" />
              )}
              <div className="glass-card p-5 h-full hover:border-violet-500/30 transition-colors duration-200">
                <div className="text-3xl font-black gradient-text mb-3">{step.step}</div>
                <h3 className="font-bold text-white text-sm mb-2">{step.title}</h3>
                <p className="text-xs text-gray-400 leading-relaxed">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── CTA Banner ───────────────────────────────────────── */}
      <section className="max-w-4xl mx-auto px-6 mb-20">
        <div className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-violet-900/50 to-cyan-900/50 border border-violet-500/20 p-10 text-center">
          <div className="absolute inset-0 bg-gradient-to-br from-violet-600/10 to-cyan-600/10" />
          <div className="relative">
            <Star size={32} className="text-yellow-400 mx-auto mb-4 animate-float" />
            <h2 className="text-3xl font-black text-white mb-3">
              Ready to find your perfect deal?
            </h2>
            <p className="text-gray-400 mb-6 max-w-md mx-auto">
              Browse 50+ analyzed listings across 10 Indian cities, ranked by deal score.
            </p>
            <Link href="/deals" id="cta-browse-deals-btn" className="btn-primary px-10 py-4 text-base">
              Browse All Deals <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
