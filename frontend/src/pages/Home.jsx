import React, { useState, useEffect, useCallback } from 'react';
import Navbar from '../components/Navbar.jsx';
import ProductSelector from '../components/ProductSelector.jsx';
import RecommendationGrid from '../components/RecommendationGrid.jsx';
import KnowledgeGraph from '../components/KnowledgeGraph.jsx';
import ExplanationPanel from '../components/ExplanationPanel.jsx';
import ProductDetailModal from '../components/ProductDetailModal.jsx';
import LoadingState from '../components/LoadingState.jsx';
import EmptyState from '../components/EmptyState.jsx';
import ErrorState from '../components/ErrorState.jsx';
import { getProducts, getRecommendations, getProductDetails, getHealth } from '../services/api.js';
import { FALLBACK_PRODUCTS } from '../data/fallbackProducts.js';

export default function Home() {
  // Products catalog state
  const [products, setProducts] = useState([]);
  const [usingFallback, setUsingFallback] = useState(false);
  const [apiHealthy, setApiHealthy] = useState(true);

  // User selection & recommendation state
  const [selectedProduct, setSelectedProduct] = useState('');
  const [topK, setTopK] = useState(5);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Modals state
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [isExplanationOpen, setIsExplanationOpen] = useState(false);
  const [productDetailModal, setProductDetailModal] = useState({
    isOpen: false,
    loading: false,
    data: null,
  });

  // Selected product metadata for graph visualization
  const [selectedProductMeta, setSelectedProductMeta] = useState(null);

  // Fetch initial products catalog and verify API health
  const fetchProductsList = useCallback(async () => {
    setError(null);
    try {
      // Check health
      try {
        await getHealth();
        setApiHealthy(true);
      } catch (healthErr) {
        console.warn('API health check warning:', healthErr);
        setApiHealthy(false);
      }

      const data = await getProducts();
      if (Array.isArray(data) && data.length > 0) {
        setProducts(data);
        setUsingFallback(false);
        // Pre-select first product if none selected
        if (!selectedProduct) {
          const first = typeof data[0] === 'string' ? data[0] : data[0].name;
          setSelectedProduct(first);
        }
      } else {
        throw new Error('No products returned from API');
      }
    } catch (err) {
      console.warn('Failed to fetch /products from backend, falling back to static catalog:', err);
      setProducts(FALLBACK_PRODUCTS);
      setUsingFallback(true);
      if (!selectedProduct) {
        setSelectedProduct(FALLBACK_PRODUCTS[0]);
      }
    }
  }, [selectedProduct]);

  useEffect(() => {
    fetchProductsList();
  }, [fetchProductsList]);

  // When selected product changes, fetch its metadata for the Knowledge Graph visualization
  useEffect(() => {
    if (!selectedProduct) {
      setSelectedProductMeta(null);
      return;
    }

    let isMounted = true;
    getProductDetails(selectedProduct)
      .then((data) => {
        if (isMounted) setSelectedProductMeta(data);
      })
      .catch((err) => {
        console.warn('Could not load details for selected product:', err);
        if (isMounted) setSelectedProductMeta(null);
      });

    return () => {
      isMounted = false;
    };
  }, [selectedProduct]);

  // Request recommendations from FastAPI /recommend/{product_name}
  const handleGetRecommendations = async () => {
    if (!selectedProduct) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getRecommendations(selectedProduct, topK);
      if (data && Array.isArray(data.recommendations)) {
        setRecommendations(data.recommendations);
        setApiHealthy(true);
      } else {
        throw new Error('Unexpected recommendation payload format from API');
      }
    } catch (err) {
      console.error('Failed to get recommendations:', err);
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to connect to the recommendation engine.'
      );
      setRecommendations(null);
      setApiHealthy(false);
    } finally {
      setLoading(false);
    }
  };

  // Open explanation modal
  const handleViewExplanation = (recommendationItem) => {
    setSelectedRecommendation(recommendationItem);
    setIsExplanationOpen(true);
  };

  // Open product detail modal
  const handleViewProductDetails = async (productName) => {
    setProductDetailModal({ isOpen: true, loading: true, data: null });
    try {
      const details = await getProductDetails(productName);
      setProductDetailModal({ isOpen: true, loading: false, data: details });
    } catch (err) {
      console.error('Failed to get product details:', err);
      // Fallback object so modal still displays gracefully
      setProductDetailModal({
        isOpen: true,
        loading: false,
        data: { name: productName, description: 'Details not available.' },
      });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Top Navbar */}
      <Navbar apiHealthy={apiHealthy} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
        {/* Hero & Selection Form */}
        <ProductSelector
          products={products}
          selectedProduct={selectedProduct}
          onSelectProduct={(val) => {
            setSelectedProduct(val);
            setRecommendations(null); // Reset recommendations when selection changes
            setError(null);
          }}
          onGetRecommendations={handleGetRecommendations}
          loading={loading}
          topK={topK}
          onChangeTopK={setTopK}
          onViewProductDetails={handleViewProductDetails}
          usingFallback={usingFallback}
        />

        {/* Dynamic Display Area based on State */}
        {loading && <LoadingState />}

        {!loading && error && (
          <ErrorState
            error={error}
            onRetry={handleGetRecommendations}
            apiUrl={import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'}
          />
        )}

        {!loading && !error && recommendations === null && (
          <EmptyState />
        )}

        {!loading && !error && recommendations !== null && (
          <>
            {/* Recommendations Grid */}
            <RecommendationGrid
              purchasedProduct={selectedProduct}
              recommendations={recommendations}
              onViewExplanation={handleViewExplanation}
              onProductClick={handleViewProductDetails}
            />

            {/* Knowledge Graph Subgraph and Reasoning Breakdown */}
            <KnowledgeGraph
              selectedProduct={selectedProduct}
              recommendations={recommendations}
              productDetails={selectedProductMeta}
            />
          </>
        )}
      </main>

      {/* Explanation Modal */}
      <ExplanationPanel
        isOpen={isExplanationOpen}
        onClose={() => {
          setIsExplanationOpen(false);
          setSelectedRecommendation(null);
        }}
        purchasedProduct={selectedProduct}
        recommendation={selectedRecommendation}
      />

      {/* Product Detail Modal */}
      <ProductDetailModal
        isOpen={productDetailModal.isOpen}
        loading={productDetailModal.loading}
        productDetails={productDetailModal.data}
        onClose={() => setProductDetailModal({ isOpen: false, loading: false, data: null })}
        onSelectAsPurchased={(name) => {
          setSelectedProduct(name);
          setRecommendations(null);
        }}
      />

      {/* Modern SaaS Footer */}
      <footer className="mt-16 border-t border-slate-200 bg-white py-8 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2 font-medium text-slate-700">
            <span className="w-2 h-2 rounded-full bg-blue-600"></span>
            <span>ShopGraph — Knowledge Graph Recommendation Engine</span>
          </div>
          <div>
            Powered by Neo4j Knowledge Graph &bull; FastAPI &bull; React &bull; Tailwind CSS
          </div>
        </div>
      </footer>
    </div>
  );
}
