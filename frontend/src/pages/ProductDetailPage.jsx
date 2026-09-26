import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ShoppingCart, Tag, CheckCircle, Zap, Package, Layers, ArrowLeft } from 'lucide-react';
import { productsAPI, eventsAPI, recommendationsAPI } from '../services/api.js';
import RecommendationSection from '../components/RecommendationSection.jsx';
import { useCart } from '../context/CartContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';

export default function ProductDetailPage() {
  const { productName } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { addToCart, fetchCart } = useCart();

  const decodedName = decodeURIComponent(productName);

  const [product, setProduct] = useState(null);
  const [loadingProduct, setLoadingProduct] = useState(true);
  const [productError, setProductError] = useState(null);

  const [recommendations, setRecommendations] = useState(null);
  const [loadingRecs, setLoadingRecs] = useState(false);

  const [addingToCart, setAddingToCart] = useState(false);
  const [addedToCart, setAddedToCart] = useState(false);

  // Fetch product details
  useEffect(() => {
    setLoadingProduct(true);
    setProductError(null);
    productsAPI.getOne(decodedName)
      .then(setProduct)
      .catch((err) => {
        setProductError(err.response?.data?.detail || 'Product not found');
      })
      .finally(() => setLoadingProduct(false));
  }, [decodedName]);

  // Auto-record VIEW event and fetch recommendations when product loads
  useEffect(() => {
    if (!product) return;

    // Record VIEW event automatically (no button needed)
    eventsAPI.record('VIEW', product.name);

    // Automatically fetch recommendations
    setLoadingRecs(true);
    recommendationsAPI.forProduct(product.name, 5)
      .then(setRecommendations)
      .catch(console.error)
      .finally(() => setLoadingRecs(false));
  }, [product]);

  // Fetch cart when user changes
  useEffect(() => {
    if (user) fetchCart();
  }, [user, fetchCart]);

  const handleAddToCart = async () => {
    if (!user) { navigate('/login'); return; }
    setAddingToCart(true);
    try {
      await addToCart(product.name, product.price, 1);
      setAddedToCart(true);
      setTimeout(() => setAddedToCart(false), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setAddingToCart(false);
    }
  };

  if (loadingProduct) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
        <p className="mt-4 text-slate-500">Loading product...</p>
      </div>
    );
  }

  if (productError || !product) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <p className="text-red-500 font-medium">{productError || 'Product not found'}</p>
        <button onClick={() => navigate('/products')} className="mt-4 text-blue-600 hover:underline">← Back to Products</button>
      </div>
    );
  }

  const sections = recommendations?.sections || {};

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-sm text-slate-500 hover:text-blue-600 mb-6">
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      {/* Product Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 lg:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image */}
          <div className="h-64 lg:h-80 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl flex items-center justify-center">
            <span className="text-8xl font-bold text-blue-200">{product.name.charAt(0)}</span>
          </div>

          {/* Details */}
          <div>
            {product.category && (
              <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
                {product.category}
              </span>
            )}
            <h1 className="text-2xl font-bold text-slate-800 mt-3">{product.name}</h1>
            {product.brand && <p className="text-slate-400 text-sm mt-1">by {product.brand}</p>}
            
            <div className="text-3xl font-bold text-slate-800 mt-4">
              {product.price ? `₹${product.price.toLocaleString('en-IN')}` : 'Price unavailable'}
            </div>

            {product.description && (
              <p className="text-slate-600 text-sm mt-4 leading-relaxed">{product.description}</p>
            )}

            {/* Features */}
            {product.features?.length > 0 && (
              <div className="mt-4">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Features</h3>
                <div className="flex flex-wrap gap-2">
                  {product.features.map(f => (
                    <span key={f} className="text-xs bg-slate-100 text-slate-600 px-2 py-1 rounded-full">{f}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Use Cases */}
            {product.use_cases?.length > 0 && (
              <div className="mt-3">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Use Cases</h3>
                <div className="flex flex-wrap gap-2">
                  {product.use_cases.map(u => (
                    <span key={u} className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full">{u}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Add to Cart */}
            <div className="mt-6 flex gap-3">
              <button
                onClick={handleAddToCart}
                disabled={addingToCart}
                className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-semibold transition-all ${
                  addedToCart
                    ? 'bg-green-500 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                } disabled:opacity-60`}
              >
                {addedToCart ? (
                  <><CheckCircle className="w-4 h-4" /> Added to Cart!</>
                ) : addingToCart ? (
                  'Adding...'
                ) : (
                  <><ShoppingCart className="w-4 h-4" /> Add to Cart</>
                )}
              </button>
            </div>

            {!user && (
              <p className="text-xs text-slate-400 mt-2 text-center">
                <Link to="/login" className="text-blue-600 hover:underline">Login</Link> to add items to cart
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Recommendation Sections — Auto-generated, NO manual button */}
      <div className="mt-8 space-y-2">
        <RecommendationSection
          title="✨ You May Also Like"
          recommendations={sections.you_may_also_like}
          loading={loadingRecs}
          contextLabel="Similar product"
        />

        <RecommendationSection
          title="🔗 Compatible With"
          recommendations={sections.compatible_with}
          loading={false}
          emptyMessage={null}
          contextLabel="Compatible"
        />

        <RecommendationSection
          title="🎒 Recommended Accessories"
          recommendations={sections.accessories}
          loading={false}
          emptyMessage={null}
          contextLabel="Accessory"
        />
      </div>
    </div>
  );
}
