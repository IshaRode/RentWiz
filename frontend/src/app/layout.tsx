import type { Metadata } from 'next';
import { Inter, Geist } from 'next/font/google';
import './globals.css';
import Link from 'next/link';
import { cn } from "@/lib/utils";
import Logo from '@/components/Logo';
import LiquidEtherWrapper from '@/components/LiquidEtherWrapper';
import Navbar from '@/components/Navbar';

const geist = Geist({ subsets: ['latin'], variable: '--font-sans' });

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
      <body className="min-h-screen text-white antialiased">
        {/* LiquidEther Background */}
        <LiquidEtherWrapper />

        <div className="relative z-10 flex flex-col min-h-screen">
          {/* Navigation */}
          <Navbar />

          {/* Main */}
          <main className="pt-16 flex-1">{children}</main>

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
        </div>
      </body>
    </html>
  );
}
