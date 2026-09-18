# ShopGraph Frontend

A clean, modern product recommendation dashboard built with **React**, **Vite**, and **Tailwind CSS**. It connects directly to the FastAPI recommendation engine and Neo4j Knowledge Graph.

---

## Features

- **Product Selector**: Pulls catalog products dynamically from `GET /products`.
- **Knowledge Graph Recommendations**: Triggers `GET /recommend/{product_name}?top_k={top_k}` to compute explainable recommendations based on graph traversal.
- **Explainable Evidence Modal**: Visualizes the graph path and displays human-readable reasons (shared features, direct compatibility, use cases) directly from the recommendation engine.
- **Interactive SVG Knowledge Graph**: Renders the active subgraph (Purchased Product $\leftrightarrow$ Features $\leftrightarrow$ Recommendations $\leftrightarrow$ Use Cases).
- **Algorithmic Reasoning Pipeline**: Explains the step-by-step scoring logic (Relationships, Features, Categories, Use Cases, Similarity).
- **Product Details Modal**: Displays full product metadata from `GET /products/{product_name}`.
- **Resilient States**: Beautiful loading skeletons, informative empty states, and connection error handling with retry capability.

---

## Prerequisites

- **Node.js**: v18 or higher (v20+ recommended)
- **FastAPI Backend**: Running at `http://127.0.0.1:8000`

---

## Getting Started

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file in the `frontend/` directory (or copy from `.env.example`):

```env
VITE_API_URL=http://127.0.0.1:8000
```

### 3. Start Development Server

```bash
npm run dev
```

Open your browser at:
```text
http://localhost:5173
```

### 4. Build for Production

```bash
npm run build
```

This generates optimized production assets in the `dist/` directory.

---

## Project Structure

```text
frontend/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── .env
├── .env.example
├── README.md
└── src/
    ├── main.jsx
    ├── index.css
    ├── App.jsx
    ├── components/
    │   ├── Navbar.jsx               # Header with brand and API status
    │   ├── ProductSelector.jsx      # Product picker and recommendation trigger
    │   ├── RecommendationCard.jsx   # Individual recommendation card
    │   ├── RecommendationGrid.jsx   # Responsive recommendation grid
    │   ├── ScoreBadge.jsx           # Transparent match score indicator
    │   ├── ExplanationPanel.jsx     # Knowledge Graph evidence modal
    │   ├── KnowledgeGraph.jsx       # SVG subgraph & reasoning pipeline
    │   ├── ProductDetailModal.jsx   # Full product node details modal
    │   ├── LoadingState.jsx         # Loading spinner and skeleton
    │   ├── EmptyState.jsx           # Initial prompt before search
    │   └── ErrorState.jsx           # API failure recovery view
    ├── pages/
    │   └── Home.jsx                 # Main dashboard page
    ├── services/
    │   └── api.js                   # Axios client for FastAPI endpoints
    └── data/
        └── fallbackProducts.js      # Offline fallback catalog
```
