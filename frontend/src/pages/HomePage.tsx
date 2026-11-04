import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Database, Zap, Cpu, CheckCircle2 } from 'lucide-react';
import { HouseIllustration } from '../components/HouseIllustration';

export const HomePage: React.FC = () => {
  return (
    <div className="w-full min-h-full py-6 sm:py-10 md:py-14 lg:py-18">
      <div className="page-container">
        
        {/* HERO SECTION */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 sm:gap-10 lg:gap-12 xl:gap-16 items-center mb-12 sm:mb-16 lg:mb-20">
          
          {/* Hero Left Content */}
          <div className="lg:col-span-7 xl:col-span-7 space-y-4 sm:space-y-6 text-left">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full border border-[#E5E5E5] bg-[#FFFFFF] text-[11px] font-medium text-[#737373]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#171717]"></span>
              <span>Machine Learning Rental Valuation</span>
            </div>

            <h1 className="text-2xl sm:text-4xl md:text-5xl lg:text-5xl xl:text-6xl font-bold tracking-tight text-[#171717] leading-[1.15]">
              Know the Right Price Before You Host.
            </h1>

            <p className="text-sm sm:text-base md:text-lg text-[#737373] leading-relaxed max-w-2xl">
              An intelligent Airbnb pricing assistant that estimates nightly rental prices using property characteristics and machine learning.
            </p>

            {/* Hero CTAs - Full width on small mobile, auto on sm+ */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center space-y-3 sm:space-y-0 sm:space-x-4 pt-1 sm:pt-2">
              <Link
                to="/predict"
                className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 bg-[#333333] hover:bg-[#1f1f1f] text-white text-xs sm:text-sm font-medium px-6 py-3.5 rounded-xl transition-all shadow-sm"
              >
                <span>Predict My Property Price</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              <Link
                to="/how-it-works"
                className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 bg-[#FFFFFF] hover:bg-[#F9F9F9] text-[#171717] text-xs sm:text-sm font-medium px-6 py-3.5 rounded-xl border border-[#E5E5E5] transition-colors"
              >
                <span>How It Works</span>
              </Link>
            </div>

            {/* Subtle verification points */}
            <div className="pt-2 sm:pt-4 flex flex-wrap items-center gap-3 sm:gap-5 text-xs text-[#737373]">
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#171717] flex-shrink-0" />
                <span>6 Major US Markets</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#171717] flex-shrink-0" />
                <span>13 Key Amenity Factors</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#171717] flex-shrink-0" />
                <span>Log-Price Regression</span>
              </div>
            </div>
          </div>

          {/* Hero Right: Monochrome House Illustration */}
          <div className="lg:col-span-5 xl:col-span-5 flex justify-center w-full">
            <div className="w-full bg-[#FFFFFF] border border-[#E5E5E5] rounded-2xl p-4 sm:p-6 md:p-8 shadow-sm flex items-center justify-center">
              <HouseIllustration className="w-full" />
            </div>
          </div>
        </div>

        {/* SECTION: 3 KEY PILLARS */}
        <div className="pt-4 border-t border-[#E5E5E5]">
          <div className="text-center max-w-2xl mx-auto mb-8 sm:mb-12 pt-6 sm:pt-8">
            <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-[#171717] tracking-tight">
              Designed for Confident Hosting
            </h2>
            <p className="text-xs sm:text-sm text-[#737373] mt-2">
              Combining real-world Airbnb listing attributes with rigorous predictive regression modeling.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
            
            {/* Pillar 1: Data-Driven */}
            <div className="bg-[#FFFFFF] border border-[#E5E5E5] rounded-xl p-5 sm:p-6 transition-all hover:border-[#CCCCCC] flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-lg bg-[#FAFAFA] border border-[#E5E5E5] flex items-center justify-center text-[#171717] mb-4">
                  <Database className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-[#171717] mb-2">
                  Data-Driven
                </h3>
                <p className="text-xs text-[#737373] leading-relaxed">
                  Trained on real-world Kaggle Airbnb listings across NYC, LA, SF, DC, Chicago, and Boston. Captures actual market trends rather than rough host guesswork.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-[#F0F0F0] text-[11px] text-[#737373]">
                Features: Accommodates, Bedrooms, Bathrooms & City
              </div>
            </div>

            {/* Pillar 2: Quick & Easy */}
            <div className="bg-[#FFFFFF] border border-[#E5E5E5] rounded-xl p-5 sm:p-6 transition-all hover:border-[#CCCCCC] flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-lg bg-[#FAFAFA] border border-[#E5E5E5] flex items-center justify-center text-[#171717] mb-4">
                  <Zap className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-[#171717] mb-2">
                  Quick & Easy
                </h3>
                <p className="text-xs text-[#737373] leading-relaxed">
                  Enter your property details in under 60 seconds. Customize room types, bed configurations, cleaning fees, and select available amenities with instant feedback.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-[#F0F0F0] text-[11px] text-[#737373]">
                Zero setup: Instant estimated dollar price
              </div>
            </div>

            {/* Pillar 3: Backed by ML */}
            <div className="bg-[#FFFFFF] border border-[#E5E5E5] rounded-xl p-5 sm:p-6 transition-all hover:border-[#CCCCCC] flex flex-col justify-between sm:col-span-2 lg:col-span-1">
              <div>
                <div className="w-10 h-10 rounded-lg bg-[#FAFAFA] border border-[#E5E5E5] flex items-center justify-center text-[#171717] mb-4">
                  <Cpu className="w-5 h-5" />
                </div>
                <h3 className="text-base font-semibold text-[#171717] mb-2">
                  Backed by ML
                </h3>
                <p className="text-xs text-[#737373] leading-relaxed">
                  Engineered with scikit-learn Linear Regression, log-price target transformation, and ColumnTransformer one-hot encodings to eliminate skew and deliver accurate rates.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-[#F0F0F0] text-[11px] text-[#737373]">
                Pipeline: Imputer + OneHot + LinearRegressor
              </div>
            </div>

          </div>
        </div>

        {/* BOTTOM QUICK CALLOUT BANNER */}
        <div className="mt-10 sm:mt-14 bg-[#FFFFFF] border border-[#E5E5E5] rounded-2xl p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-1 text-center md:text-left">
            <h3 className="text-base sm:text-lg font-bold text-[#171717]">
              Ready to value your listing?
            </h3>
            <p className="text-xs sm:text-sm text-[#737373]">
              Configure your room setup, select amenities, and calculate your target nightly rate.
            </p>
          </div>
          <Link
            to="/predict"
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 bg-[#333333] hover:bg-[#1f1f1f] text-white text-xs sm:text-sm font-semibold px-6 py-3 rounded-xl transition-colors whitespace-nowrap shadow-sm"
          >
            <span>Launch Prediction Form</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

      </div>
    </div>
  );
};
