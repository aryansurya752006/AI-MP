import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { PredictionProvider } from './context/PredictionContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';

import { HomePage } from './pages/HomePage';
import { PredictPage } from './pages/PredictPage';
import { ResultsPage } from './pages/ResultsPage';
import { HowItWorksPage } from './pages/HowItWorksPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { AboutModelPage } from './pages/AboutModelPage';

export function App() {
  return (
    <PredictionProvider>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col bg-[#F5F5F5] text-[#171717]">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/predict" element={<PredictPage />} />
              <Route path="/results" element={<ResultsPage />} />
              <Route path="/how-it-works" element={<HowItWorksPage />} />
              <Route path="/model-performance" element={<ModelPerformancePage />} />
              <Route path="/about-model" element={<AboutModelPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </BrowserRouter>
    </PredictionProvider>
  );
}

export default App;
