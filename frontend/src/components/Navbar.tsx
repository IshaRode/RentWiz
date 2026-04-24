'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Logo from '@/components/Logo';
import { Menu, X } from 'lucide-react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  // Close the menu automatically when navigating to a new page
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#050816]/75 backdrop-blur-2xl border-b border-violet-500/10">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center group">
          <Logo />
        </Link>

        {/* Desktop Nav */}
        <div className="hidden md:flex items-center gap-1">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/deals" className="nav-link">Best Deals</Link>
          <Link href="/insights" className="nav-link">Market Insights</Link>
        </div>

        <div className="w-[100px] hidden sm:block md:hidden lg:block"></div>

        {/* Mobile Hamburger Button */}
        <button 
          className="md:hidden p-2 -mr-2 text-gray-400 hover:text-white focus:outline-none"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle menu"
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Nav Dropdown */}
      {isOpen && (
        <div className="md:hidden absolute top-16 left-0 right-0 bg-[#050816]/95 backdrop-blur-xl border-b border-violet-500/10 p-6 flex flex-col gap-5 shadow-2xl">
          <Link href="/" className="text-base font-semibold text-gray-300 hover:text-white transition-colors">
            Home
          </Link>
          <Link href="/deals" className="text-base font-semibold text-gray-300 hover:text-white transition-colors">
            Best Deals
          </Link>
          <Link href="/insights" className="text-base font-semibold text-gray-300 hover:text-white transition-colors">
            Market Insights
          </Link>
        </div>
      )}
    </nav>
  );
}
