import React from 'react';
import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-[#FFFFFF] border-t border-[#E5E5E5] mt-auto w-full">
      <div className="page-container py-8 sm:py-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 mb-8">
          <div className="sm:col-span-2 space-y-3">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 rounded-md bg-[#333333] flex items-center justify-center text-white">
                <Home className="w-3.5 h-3.5" />
              </div>
              <span className="font-semibold text-sm text-[#171717]">StayWise AI</span>
            </div>
            <p className="text-xs text-[#737373] max-w-md leading-relaxed">
              Intelligent Airbnb nightly rate estimation using supervised machine learning,
              interpretable feature weights, and historical market listing data.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-[#171717] uppercase tracking-wider mb-3">
              Application
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/" className="text-[#737373] hover:text-[#171717] transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/predict" className="text-[#737373] hover:text-[#171717] transition-colors">
                  Predict Price
                </Link>
              </li>
              <li>
                <Link to="/results" className="text-[#737373] hover:text-[#171717] transition-colors">
                  Results View
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-[#171717] uppercase tracking-wider mb-3">
              Machine Learning
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link to="/how-it-works" className="text-[#737373] hover:text-[#171717] transition-colors">
                  How It Works
                </Link>
              </li>
              <li>
                <Link to="/about-model" className="text-[#737373] hover:text-[#171717] transition-colors">
                  About Model
                </Link>
              </li>
              <li>
                <Link to="/model-performance" className="text-[#737373] hover:text-[#171717] transition-colors">
                  Model Performance
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-[#E5E5E5] flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#737373] gap-2">
          <p>© {new Date().getFullYear()} StayWise AI. Built with React, TypeScript & Tailwind CSS.</p>
          <p>Dataset: Kaggle Airbnb Price Prediction</p>
        </div>
      </div>
    </footer>
  );
};
