import type { Metadata } from 'next';
import { Inter, Geist } from 'next/font/google';
import './globals.css';
import Link from 'next/link';
import { cn } from "@/lib/utils";
import Logo from '@/components/Logo';

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'RentWiz – AI Rental Deal Finder',
  description:
    'Discover underpriced rental properties in Indian cities using AI-powered fair-rent prediction. Find great deals on 1BHK, 2BHK, 3BHK apartments.',
  keywords: 'rental deals, rent prediction, AI rental, Mumbai rent, Delhi rent, Bangalore rent, underpriced apartments',
  openGraph: {
    title: 'RentWiz – AI Rental Deal Finder',
    description: 'Find rental properties priced below fair market value using machine learning.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={cn("font-sans", geist.variable)}>
      <body className="min-h-screen bg-[#0a0f1e] text-white antialiased">
        {/* Navigation */}
        <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0a0f1e]/80 backdrop-blur-xl border-b border-white/5">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <Link href="/" className="flex items-center group">
              <Logo />
            </Link>

            <div className="hidden md:flex items-center gap-1">
              <Link href="/" className="nav-link">Home</Link>
              <Link href="/deals" className="nav-link">Best Deals</Link>
              <Link href="/insights" className="nav-link">Market Insights</Link>
            </div>

            <div className="flex items-center gap-3">
              <span className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-400/10 px-3 py-1.5 rounded-full border border-emerald-400/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live Data
              </span>
            </div>
          </div>
        </nav>

        {/* Main */}
        <main className="pt-16">{children}</main>

        {/* Footer */}
        <footer className="border-t border-white/5 py-10 mt-20">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-gray-500 text-sm">
              <span className="text-lg font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">RentWiz</span>
              <span>·</span>
              <span>AI-powered rental deal finder</span>
            </div>
            <p className="text-xs text-gray-600">
              Predictions are for informational purposes only. Always verify with listings directly.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
