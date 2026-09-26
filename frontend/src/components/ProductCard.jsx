import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, ShoppingCart, Heart, Check } from 'lucide-react';
import { useCart } from '../context/CartContext.jsx';
import { useWishlist } from '../context/WishlistContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { getProductImageUrl, handleImageError } from '../utils/imageHelper.js';

export default function ProductCard({ product, reason }) {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { isWishlisted, toggleWishlist } = useWishlist();
  const { user } = useAuth();

  const [isAdding, setIsAdding] = useState(false);
  const [justAdded, setJustAdded] = useState(false);

  if (!product) return null;

  const {
    name,
    price,
    original_price,
    discount_percentage,
    category,
    brand,
    rating = 4.5,
    review_count = 120,
    stock = 25,
  } = product;

  const wishlisted = isWishlisted(name);
  const imageUrl = getProductImageUrl(product);

  const handleClick = () => {
    navigate(`/products/${encodeURIComponent(name)}`);
  };

  const handleAddToCart = async (e) => {
    e.stopPropagation();
    if (!user) {
      navigate('/login');
      return;
    }
    setIsAdding(true);
    try {
      await addToCart(name, price, 1);
      setJustAdded(true);
      setTimeout(() => setJustAdded(false), 2000);
    } catch (err) {
      console.error('Add to cart failed:', err);
    } finally {
      setIsAdding(false);
    }
  };

  const handleWishlistClick = async (e) => {
    e.stopPropagation();
    if (!user) {
      navigate('/login');
      return;
    }
    await toggleWishlist(product);
  };

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-2xl border border-slate-200 hover:border-blue-400 hover:shadow-xl transition-all duration-300 flex flex-col justify-between overflow-hidden cursor-pointer group relative"
    >
      {/* Top Image Container */}
      <div className="relative w-full h-48 bg-slate-50 overflow-hidden flex items-center justify-center p-3">
        <img
          src={imageUrl}
          alt={name}
          onError={(e) => handleImageError(e, category, name)}
          className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />

        {/* Wishlist Button */}
        <button
          onClick={handleWishlistClick}
          aria-label={wishlisted ? 'Remove from wishlist' : 'Add to wishlist'}
          className={`absolute top-2.5 right-2.5 w-8 h-8 rounded-full flex items-center justify-center transition-all shadow-sm ${
            wishlisted
              ? 'bg-rose-50 text-rose-600 hover:bg-rose-100'
              : 'bg-white/90 backdrop-blur-sm text-slate-400 hover:text-rose-500 hover:bg-white'
          }`}
        >
          <Heart className={`w-4 h-4 ${wishlisted ? 'fill-rose-500 text-rose-500' : ''}`} />
        </button>

        {/* Discount Badge */}
        {discount_percentage > 0 && (
          <span className="absolute top-2.5 left-2.5 bg-emerald-600 text-white font-bold text-[10px] px-2 py-0.5 rounded-full shadow-sm">
            {discount_percentage}% OFF
          </span>
        )}
      </div>

      {/* Product Details */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          {/* Brand & Category */}
          <div className="flex items-center justify-between gap-2 text-xs">
            <span className="font-semibold text-blue-600 uppercase tracking-wider text-[10px]">
              {brand || 'ShopGraph'}
            </span>
            {category && (
              <span className="text-slate-400 text-[11px] truncate">{category}</span>
            )}
          </div>

          {/* Product Name */}
          <h3 className="font-medium text-slate-800 text-sm mt-1 leading-snug line-clamp-2 group-hover:text-blue-600 transition-colors">
            {name}
          </h3>

          {/* Rating & Reviews */}
          <div className="flex items-center gap-1.5 mt-1.5">
            <div className="flex items-center gap-0.5 bg-amber-50 text-amber-700 px-1.5 py-0.5 rounded text-[11px] font-semibold">
              <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
              <span>{rating.toFixed(1)}</span>
            </div>
            <span className="text-xs text-slate-400">({review_count})</span>
          </div>

          {/* Recommendation Reason Pill */}
          {reason && (
            <p className="mt-2 text-[11px] text-indigo-700 bg-indigo-50 border border-indigo-100 rounded-md px-2 py-1 leading-tight line-clamp-1">
              ✨ {reason}
            </p>
          )}
        </div>

        {/* Price & Action Row */}
        <div className="mt-3 pt-3 border-t border-slate-100">
          <div className="flex items-baseline gap-2">
            <span className="text-base font-bold text-slate-900">
              ₹{price ? price.toLocaleString('en-IN') : 'N/A'}
            </span>
            {original_price && original_price > price && (
              <span className="text-xs text-slate-400 line-through">
                ₹{original_price.toLocaleString('en-IN')}
              </span>
            )}
          </div>

          {/* Add to Cart CTA */}
          <button
            onClick={handleAddToCart}
            disabled={isAdding}
            className={`w-full mt-2.5 py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all shadow-sm ${
              justAdded
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-900 text-white hover:bg-blue-600 active:scale-[0.98]'
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
                <span>{isAdding ? 'Adding...' : 'Add to Cart'}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
