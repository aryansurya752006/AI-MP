# StayWise AI — Frontend Application

Modern React + TypeScript web application for predicting Airbnb nightly rental prices using machine learning.

---

## 📁 Project Architecture & Directory Structure

```text
frontend/
├── public/                     # Static assets (favicons, SVG icons)
├── src/
│   ├── assets/                 # SVGs and graphic illustrations
│   ├── components/             # Reusable UI presentation components
│   │   ├── Footer.tsx          # Minimal sticky footer (@ ARYAN SURYA S)
│   │   ├── HouseIllustration.tsx # Architectural monochrome house vector
│   │   ├── Navbar.tsx          # Sticky top navigation bar
│   │   ├── ScrollToTop.tsx     # Route-change auto-scroll utility
│   │   └── index.ts            # Components barrel export
│   ├── context/                # React Context for global state
│   │   ├── PredictionContext.tsx # Context definition & interface
│   │   ├── PredictionProvider.tsx # State management with sessionStorage persistence
│   │   ├── usePrediction.ts    # Custom hook
│   │   └── index.ts            # Context barrel export
│   ├── data/                   # Dataset feature metadata and options
│   │   └── datasetInfo.ts      # Cities, amenities, property types, defaults
│   ├── pages/                  # Route view components
│   │   ├── HomePage.tsx        # Centered landing view with primary CTA
│   │   ├── PredictPage.tsx     # Interactive multi-field prediction form
│   │   ├── ResultsPage.tsx     # Estimated price card, breakdown & summary
│   │   ├── HowItWorksPage.tsx  # ML pipeline walkthrough & code snippets
│   │   ├── AboutModelPage.tsx  # Log-regression architecture & feature weights
│   │   ├── ModelPerformancePage.tsx # Evaluation metrics & diagnostic plot
│   │   └── index.ts            # Pages barrel export
│   ├── services/               # API clients & client-side inference fallback
│   │   └── api.ts              # Model inference & evaluation fetching
│   ├── types/                  # TypeScript interface definitions
│   │   └── index.ts            # PredictionRequest, PredictionResponse, etc.
│   ├── App.css                 # Custom utility styles
│   ├── App.tsx                 # Root router and application layout
│   ├── index.css               # Global Tailwind CSS & typography setup
│   └── main.tsx                # React DOM root entry point
├── index.html                  # HTML template with Google Fonts
├── package.json                # Project dependencies and npm scripts
├── tailwind.config.js          # Tailwind theme & font-family config
├── tsconfig.json               # TypeScript base configuration
└── vite.config.ts              # Vite bundler configuration
```

---

## 🚀 Available Scripts

In the `frontend` directory:

- **`npm run dev`**: Starts local development server at `http://localhost:5173/`.
- **`npm run build`**: Type-checks with `tsc -b` and builds optimized production bundle.
- **`npm run lint`**: Runs fast Oxlint checks across all TypeScript/TSX files.
- **`npm run preview`**: Previews the built production distribution locally.

---

## 🎨 Design System & Fonts

- **Display Typography**: `Archivo Black`
- **Body & Editorial**: `Zilla Slab`, `Noto Serif`
- **Palette**: Minimalist monochrome grayscale (`#FFFFFF`, `#F5F5F5`, `#171717`, `#737373`, `#E5E5E5`)
