import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, ChevronDown, ChevronUp, ShoppingCart, Heart, Star, Sparkles, Check } from 'lucide-react';
import { useCart } from '../context/CartContext.jsx';
import { useWishlist } from '../context/WishlistContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { getProductImageUrl, handleImageError } from '../utils/imageHelper.js';

export default function RecommendationCard({ rec, contextLabel }) {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { isWishlisted, toggleWishlist } = useWishlist();
  const { user } = useAuth();

  const [showReasons, setShowReasons] = useState(false);
  const [adding, setAdding] = useState(false);
  const [justAdded, setJustAdded] = useState(false);

  if (!rec) return null;

  const { product, score, reasons = [], product_info = {} } = rec;
  const name = product || product_info.name;
  const price = product_info.price;
  const original_price = product_info.original_price;
  const discount = product_info.discount_percentage;
  const category = product_info.category;
  const brand = product_info.brand;
  const rating = product_info.rating || 4.5;
  const reviewCount = product_info.review_count || 110;

  const wishlisted = isWishlisted(name);
  const imageUrl = getProductImageUrl(product_info);

  const handleClick = () => {
    navigate(`/products/${encodeURIComponent(name)}`);
  };

  const handleAddToCart = async (e) => {
    e.stopPropagation();
    if (!user) {
      navigate('/login');
      return;
    }
    setAdding(true);
    try {
      await addToCart(name, price || null, 1);
      setJustAdded(true);
      setTimeout(() => setJustAdded(false), 2000);
    } catch (err) {
      console.error(err);
    } finally {
      setAdding(false);
    }
  };

  const handleWishlist = async (e) => {
    e.stopPropagation();
    if (!user) {
      navigate('/login');
      return;
    }
    await toggleWishlist({ name, ...product_info });
  };

  const scoreNum = Math.round(score || 75);
  const scoreBadgeColor =
    scoreNum >= 85
      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
      : scoreNum >= 70
      ? 'bg-blue-50 text-blue-700 border-blue-200'
      : 'bg-amber-50 text-amber-700 border-amber-200';

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-2xl border border-slate-200 hover:border-blue-400 hover:shadow-xl transition-all duration-300 flex flex-col justify-between overflow-hidden cursor-pointer group relative"
    >
      {/* Product Image Box */}
      <div className="relative w-full h-44 bg-slate-50 overflow-hidden flex items-center justify-center p-3">
        <img
          src={imageUrl}
          alt={name}
          onError={(e) => handleImageError(e, category, name)}
          className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />

        {/* Graph Score Badge */}
        <span
          className={`absolute top-2.5 left-2.5 text-[11px] font-bold px-2 py-0.5 rounded-full border shadow-sm flex items-center gap-1 ${scoreBadgeColor}`}
        >
          <Sparkles className="w-3 h-3" />
          {scoreNum}% Match
        </span>

        {/* Wishlist Button */}
        <button
          onClick={handleWishlist}
          aria-label={wishlisted ? 'Remove from wishlist' : 'Add to wishlist'}
          className={`absolute top-2.5 right-2.5 w-8 h-8 rounded-full flex items-center justify-center transition-all shadow-sm ${
            wishlisted
              ? 'bg-rose-50 text-rose-600 hover:bg-rose-100'
              : 'bg-white/90 backdrop-blur-sm text-slate-400 hover:text-rose-500 hover:bg-white'
          }`}
        >
          <Heart className={`w-4 h-4 ${wishlisted ? 'fill-rose-500 text-rose-500' : ''}`} />
        </button>
      </div>

      {/* Info Section */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          {contextLabel && (
            <span className="text-[10px] uppercase tracking-wider font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
              {contextLabel}
            </span>
          )}

          <div className="flex items-center justify-between text-xs text-slate-400 mt-1">
            <span className="font-semibold text-slate-600">{brand || 'Top Brand'}</span>
            {category && <span>{category}</span>}
          </div>

          <h4 className="font-medium text-sm text-slate-800 mt-1 leading-snug line-clamp-2 group-hover:text-blue-600 transition-colors">
            {name}
          </h4>

          {/* Rating */}
          <div className="flex items-center gap-1 mt-1.5">
            <div className="flex items-center gap-0.5 text-amber-500 text-xs font-semibold">
              <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              <span>{rating.toFixed(1)}</span>
            </div>
            <span className="text-xs text-slate-400">({reviewCount})</span>
          </div>

          {/* Transparent Graph Reasons */}
          {reasons && reasons.length > 0 && (
            <div className="mt-2.5 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowReasons(!showReasons);
                }}
                className="text-[11px] font-medium text-blue-600 hover:text-blue-700 flex items-center justify-between w-full"
              >
                <span>Why recommended?</span>
                {showReasons ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showReasons ? (
                <ul className="mt-1.5 space-y-1 bg-slate-50 p-2 rounded-lg border border-slate-100">
                  {reasons.slice(0, 3).map((r, i) => (
                    <li key={i} className="text-[11px] text-slate-600 flex items-start gap-1.5 leading-tight">
                      <CheckCircle2 className="w-3 h-3 text-emerald-500 mt-0.5 flex-shrink-0" />
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-[11px] text-slate-500 mt-1 truncate">
                  💡 {reasons[0]}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Pricing and Add to Cart */}
        <div className="mt-3 pt-3 border-t border-slate-100">
          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-base font-bold text-slate-900">
              {price ? `₹${price.toLocaleString('en-IN')}` : 'Check Price'}
            </span>
            {original_price && original_price > price && (
              <span className="text-xs text-slate-400 line-through">
                ₹{original_price.toLocaleString('en-IN')}
              </span>
            )}
            {discount > 0 && (
              <span className="text-[10px] font-bold text-emerald-600">
                {discount}% OFF
              </span>
            )}
          </div>

          <button
            onClick={handleAddToCart}
            disabled={adding}
            className={`w-full py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all shadow-sm ${
              justAdded
                ? 'bg-emerald-600 text-white'
                : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98]'
            }`}
          >
            {justAdded ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>Added to Cart</span>
              </>
            ) : (
              <>
                <ShoppingCart className="w-3.5 h-3.5" />
                <span>{adding ? 'Adding...' : 'Add to Cart'}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
