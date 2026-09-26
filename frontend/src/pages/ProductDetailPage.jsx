import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ShoppingCart,
  Heart,
  Star,
  CheckCircle,
  Zap,
  ArrowLeft,
  ChevronRight,
  ShieldCheck,
  Truck,
  RotateCcw,
  Sparkles,
  Layers,
} from 'lucide-react';
import { productsAPI, eventsAPI, recommendationsAPI } from '../services/api.js';
import RecommendationSection from '../components/RecommendationSection.jsx';
import { useCart } from '../context/CartContext.jsx';
import { useWishlist } from '../context/WishlistContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { getProductImageUrl, handleImageError } from '../utils/imageHelper.js';

export default function ProductDetailPage() {
  const { productName } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { addToCart, fetchCart } = useCart();
  const { isWishlisted, toggleWishlist } = useWishlist();

  const decodedName = decodeURIComponent(productName);

  const [product, setProduct] = useState(null);
  const [loadingProduct, setLoadingProduct] = useState(true);
  const [productError, setProductError] = useState(null);

  const [recData, setRecData] = useState(null);
  const [loadingRecs, setLoadingRecs] = useState(false);

  const [addingToCart, setAddingToCart] = useState(false);
  const [addedToCart, setAddedToCart] = useState(false);

  // Fetch product details
  useEffect(() => {
    setLoadingProduct(true);
    setProductError(null);
    productsAPI
      .getOne(decodedName)
      .then((data) => {
        setProduct(data);
      })
      .catch((err) => {
        setProductError(err.response?.data?.detail || 'Product not found');
      })
      .finally(() => setLoadingProduct(false));
  }, [decodedName]);

  // Record VIEW_PRODUCT event and fetch dynamic recommendations
  useEffect(() => {
    if (!product) return;

    // Real-time event tracking
    eventsAPI.record('VIEW_PRODUCT', product.name, null, product.category);

    // Fetch dynamic recommendations
    setLoadingRecs(true);
    recommendationsAPI
      .forProduct(product.name, 6)
      .then(setRecData)
      .catch(console.error)
      .finally(() => setLoadingRecs(false));
  }, [product]);

  // Sync cart
  useEffect(() => {
    if (user) fetchCart();
  }, [user, fetchCart]);

  const handleAddToCart = async () => {
    if (!user) {
      navigate('/login');
      return;
    }
    setAddingToCart(true);
    try {
      await addToCart(product.name, product.price, 1);
      setAddedToCart(true);
      setTimeout(() => setAddedToCart(false), 2500);
    } catch (err) {
      console.error(err);
    } finally {
      setAddingToCart(false);
    }
  };

  const handleBuyNow = async () => {
    if (!user) {
      navigate('/login');
      return;
    }
    await addToCart(product.name, product.price, 1);
    navigate('/cart');
  };

  if (loadingProduct) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="animate-spin w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
        <p className="mt-4 text-slate-500 font-medium">Querying Knowledge Graph for product details...</p>
      </div>
    );
  }

  if (productError || !product) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <p className="text-red-500 font-bold text-lg">{productError || 'Product not found'}</p>
        <button
          onClick={() => navigate('/products')}
          className="mt-4 inline-flex items-center gap-1.5 text-blue-600 font-semibold hover:underline"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Products Catalog
        </button>
      </div>
    );
  }

  const wishlisted = isWishlisted(product.name);
  const imageUrl = getProductImageUrl(product);
  const specs = product.specs || {};
  const hasSpecs = Object.keys(specs).length > 0;

  const relatedProducts = recData?.related_products || recData?.sections?.you_may_also_like || [];
  const recommendedForYou = recData?.recommended_for_you || recData?.recommendations || [];
  const becauseYouViewed = recData?.because_you_viewed || {
    title: `Because You Viewed ${product.name}`,
    products: relatedProducts.slice(0, 4),
  };
  const compatibleWith = recData?.compatible_with || recData?.sections?.compatible_with || [];
  const accessories = recData?.accessories || recData?.sections?.accessories || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb Navigation */}
      <nav className="flex items-center gap-1.5 text-xs text-slate-500 mb-6 flex-wrap">
        <Link to="/" className="hover:text-blue-600">
          Home
        </Link>
        <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
        <Link to="/products" className="hover:text-blue-600">
          Products
        </Link>
        {product.category && (
          <>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
            <Link
              to={`/products?category=${encodeURIComponent(product.category)}`}
              className="hover:text-blue-600"
            >
              {product.category}
            </Link>
          </>
        )}
        <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
        <span className="font-semibold text-slate-800 truncate max-w-[200px] sm:max-w-xs">
          {product.name}
        </span>
      </nav>

      {/* Main Product Hero Box */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 lg:p-10 shadow-sm">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
          {/* Left Column: Product Image Gallery */}
          <div className="lg:col-span-5 flex flex-col items-center">
            <div className="relative w-full h-80 sm:h-96 bg-slate-50 rounded-2xl overflow-hidden p-6 flex items-center justify-center border border-slate-100 shadow-inner">
              <img
                src={imageUrl}
                alt={product.name}
                onError={(e) => handleImageError(e, product.category, product.name)}
                className="w-full h-full object-contain"
              />

              {product.discount_percentage > 0 && (
                <span className="absolute top-4 left-4 bg-emerald-600 text-white font-black text-xs px-3 py-1 rounded-full shadow-md">
                  {product.discount_percentage}% OFF
                </span>
              )}

              <button
                onClick={() => user ? toggleWishlist(product) : navigate('/login')}
                className={`absolute top-4 right-4 w-10 h-10 rounded-full flex items-center justify-center shadow-md transition-all ${
                  wishlisted
                    ? 'bg-rose-50 text-rose-600'
                    : 'bg-white/90 text-slate-400 hover:text-rose-500'
                }`}
                title="Wishlist"
              >
                <Heart className={`w-5 h-5 ${wishlisted ? 'fill-rose-500 text-rose-500' : ''}`} />
              </button>
            </div>

            {/* Value Trust Badges */}
            <div className="grid grid-cols-3 gap-3 w-full mt-4 text-center">
              <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex flex-col items-center gap-1">
                <Truck className="w-4 h-4 text-blue-600" />
                <span className="text-[11px] font-semibold text-slate-700">Free Delivery</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex flex-col items-center gap-1">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span className="text-[11px] font-semibold text-slate-700">Brand Warranty</span>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex flex-col items-center gap-1">
                <RotateCcw className="w-4 h-4 text-indigo-600" />
                <span className="text-[11px] font-semibold text-slate-700">7-Day Replacement</span>
              </div>
            </div>
          </div>

          {/* Right Column: Information & Actions */}
          <div className="lg:col-span-7 flex flex-col justify-between">
            <div>
              {/* Category & Brand Header */}
              <div className="flex items-center gap-2">
                {product.brand && (
                  <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-lg uppercase tracking-wider">
                    {product.brand}
                  </span>
                )}
                {product.category && (
                  <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">
                    {product.category}
                  </span>
                )}
              </div>

              {/* Product Title */}
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-3 leading-tight">
                {product.name}
              </h1>

              {/* Rating & Review Summary */}
              <div className="flex items-center gap-3 mt-3">
                <div className="flex items-center gap-1 bg-amber-50 text-amber-800 px-2.5 py-1 rounded-lg text-xs font-bold border border-amber-200">
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                  <span>{Number(product.rating || 4.5).toFixed(1)}</span>
                </div>
                <span className="text-xs text-slate-500 font-medium">
                  {product.review_count || 140} Ratings & Verified Reviews
                </span>
                <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                  In Stock ({product.stock || 25} units)
                </span>
              </div>

              {/* Price Details */}
              <div className="mt-5 p-4 rounded-2xl bg-slate-50 border border-slate-100">
                <div className="flex items-baseline gap-3">
                  <span className="text-3xl font-black text-slate-900">
                    ₹{product.price ? product.price.toLocaleString('en-IN') : 'Check Price'}
                  </span>
                  {product.original_price && product.original_price > product.price && (
                    <span className="text-base text-slate-400 line-through">
                      ₹{product.original_price.toLocaleString('en-IN')}
                    </span>
                  )}
                  {product.discount_percentage > 0 && (
                    <span className="text-sm font-bold text-emerald-600 bg-emerald-100/60 px-2 py-0.5 rounded-md">
                      Save {product.discount_percentage}%
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Inclusive of all taxes. Free shipping on this order.</p>
              </div>

              {/* Description */}
              {product.description && (
                <p className="text-sm text-slate-600 mt-4 leading-relaxed">
                  {product.description}
                </p>
              )}

              {/* Graph Features & Use Cases Chips */}
              <div className="mt-5 space-y-3">
                {product.features?.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                      Key Hardware & Connectivity
                    </h3>
                    <div className="flex flex-wrap gap-1.5">
                      {product.features.map((feat) => (
                        <span
                          key={feat}
                          className="text-xs font-semibold text-slate-700 bg-slate-100 px-3 py-1 rounded-full border border-slate-200"
                        >
                          {feat}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {product.use_cases?.length > 0 && (
                  <div>
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                      Optimal Use Cases
                    </h3>
                    <div className="flex flex-wrap gap-1.5">
                      {product.use_cases.map((uc) => (
                        <span
                          key={uc}
                          className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200"
                        >
                          ✓ {uc}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 pt-6 border-t border-slate-100 flex flex-col sm:flex-row gap-3">
              <button
                onClick={handleAddToCart}
                disabled={addingToCart}
                className={`flex-1 py-3.5 px-6 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-md active:scale-95 ${
                  addedToCart
                    ? 'bg-emerald-600 text-white'
                    : 'bg-slate-900 hover:bg-slate-800 text-white'
                }`}
              >
                {addedToCart ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    <span>Added to Cart!</span>
                  </>
                ) : (
                  <>
                    <ShoppingCart className="w-4 h-4" />
                    <span>{addingToCart ? 'Adding...' : 'Add to Cart'}</span>
                  </>
                )}
              </button>

              <button
                onClick={handleBuyNow}
                className="flex-1 py-3.5 px-6 rounded-2xl font-bold text-sm bg-blue-600 hover:bg-blue-700 text-white transition-all shadow-md shadow-blue-500/20 active:scale-95"
              >
                Buy Now
              </button>
            </div>
          </div>
        </div>

        {/* Specifications Table (if present) */}
        {hasSpecs && (
          <div className="mt-10 pt-8 border-t border-slate-100">
            <h3 className="text-base font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              Technical Specifications
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2 text-xs">
              {Object.entries(specs).map(([key, val]) => (
                <div key={key} className="flex justify-between py-2 border-b border-slate-100">
                  <span className="font-medium text-slate-500 capitalize">
                    {key.replace(/_/g, ' ')}
                  </span>
                  <span className="font-semibold text-slate-800">{val}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ── Dynamic Recommendation Sections Powered by Knowledge Graph ── */}
      <div className="mt-12 space-y-10">
        {/* 1. Related Products (product-centric: category, brand, alternatives) */}
        {relatedProducts && relatedProducts.length > 0 && (
          <RecommendationSection
            title="🔍 Related Products"
            recommendations={relatedProducts}
            loading={loadingRecs}
            contextLabel="Similar Specs"
          />
        )}

        {/* 2. Recommended For You (user + context-centric) */}
        {recommendedForYou && recommendedForYou.length > 0 && (
          <RecommendationSection
            title="✨ Recommended For You"
            recommendations={recommendedForYou}
            loading={loadingRecs}
            contextLabel="Top Recommendation"
          />
        )}

        {/* 3. Because You Viewed [Current Product Name] (dynamic category alternatives) */}
        {becauseYouViewed && becauseYouViewed.products?.length > 0 && (
          <RecommendationSection
            title={`💡 ${becauseYouViewed.title}`}
            recommendations={becauseYouViewed.products}
            loading={loadingRecs}
            contextLabel="Category Alternative"
          />
        )}

        {/* 4. Compatible Products (Graph: COMPATIBLE_WITH, WORKS_WITH) */}
        {compatibleWith && compatibleWith.length > 0 && (
          <RecommendationSection
            title="🔗 Verified Compatible Hardware"
            recommendations={compatibleWith}
            loading={loadingRecs}
            contextLabel="Hardware Verified"
          />
        )}

        {/* 5. Recommended Accessories (Graph: ACCESSORY) */}
        {accessories && accessories.length > 0 && (
          <RecommendationSection
            title="🎒 Recommended Accessories & Add-ons"
            recommendations={accessories}
            loading={loadingRecs}
            contextLabel="Essential Accessory"
          />
        )}
      </div>
    </div>
  );
}
