import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Menu, X, ArrowUpRight } from 'lucide-react';

export const Navbar: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { label: 'Home', path: '/' },
    { label: 'How It Works', path: '/how-it-works' },
    { label: 'About Model', path: '/about-model' },
    { label: 'Model Performance', path: '/model-performance' },
  ];

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <nav className="sticky top-0 z-50 bg-[#FFFFFF] border-b border-[#E5E5E5] w-full">
      <div className="page-container">
        <div className="flex items-center justify-between h-16 w-full">
          {/* Logo / Brand - Aligned Left */}
          <Link
            to="/"
            onClick={() => setMobileMenuOpen(false)}
            className="flex items-center space-x-2.5 text-[#171717] hover:opacity-85 transition-opacity flex-shrink-0"
          >
            <div className="w-8 h-8 rounded-lg bg-[#333333] flex items-center justify-center text-white shadow-sm">
              <Home className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-sm sm:text-base tracking-tight leading-none text-[#171717]">
                StayWise AI
              </span>
              <span className="text-[9px] sm:text-[10px] text-[#737373] tracking-wide mt-0.5">
                SMART AIRBNB PRICING
              </span>
            </div>
          </Link>

          {/* Desktop & Tablet Nav Links - Centered / Distributed */}
          <div className="hidden md:flex items-center space-x-1 lg:space-x-3">
            {navLinks.map((item) => {
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-2.5 lg:px-3.5 py-1.5 text-xs lg:text-sm font-medium rounded-lg transition-colors whitespace-nowrap ${
                    active
                      ? 'text-[#171717] bg-[#F5F5F5]'
                      : 'text-[#737373] hover:text-[#171717] hover:bg-[#F9F9F9]'
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>

          {/* Predict Price CTA Button - Aligned Right */}
          <div className="hidden md:flex items-center flex-shrink-0">
            <Link
              to="/predict"
              className="inline-flex items-center space-x-1.5 bg-[#333333] hover:bg-[#1f1f1f] text-white text-xs lg:text-sm font-medium px-4 py-2 rounded-lg transition-colors shadow-sm whitespace-nowrap"
            >
              <span>Predict Price</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Mobile Menu Toggle Button */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-[#737373] hover:text-[#171717] hover:bg-[#F5F5F5] focus:outline-none"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-[#E5E5E5] bg-[#FFFFFF] px-4 pt-3 pb-5 space-y-1.5 shadow-md">
          {navLinks.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setMobileMenuOpen(false)}
              className={`block px-3.5 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'text-[#171717] bg-[#F5F5F5]'
                  : 'text-[#737373] hover:text-[#171717] hover:bg-[#F9F9F9]'
              }`}
            >
              {item.label}
            </Link>
          ))}
          <div className="pt-2">
            <Link
              to="/predict"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full flex items-center justify-center space-x-1.5 bg-[#333333] hover:bg-[#1f1f1f] text-white text-sm font-medium px-4 py-2.5 rounded-lg transition-colors shadow-sm"
            >
              <span>Predict Price</span>
              <ArrowUpRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
};
