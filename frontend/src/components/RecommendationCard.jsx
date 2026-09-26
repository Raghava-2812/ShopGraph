import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, ChevronDown, ChevronUp, ShoppingCart } from 'lucide-react';
import { useCart } from '../context/CartContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';

export default function RecommendationCard({ rec, contextLabel }) {
  const navigate = useNavigate();
  const { addToCart } = useCart();
  const { user } = useAuth();
  const [showReasons, setShowReasons] = useState(false);
  const [adding, setAdding] = useState(false);

  const { product, score, reasons, product_info } = rec;
  const info = product_info || {};

  const handleClick = () => navigate(`/products/${encodeURIComponent(product)}`);

  const handleAddToCart = async (e) => {
    e.stopPropagation();
    if (!user) { navigate('/login'); return; }
    setAdding(true);
    try {
      await addToCart(product, info.price || null, 1);
    } catch (err) {
      console.error(err);
    } finally {
      setAdding(false);
    }
  };

  const scoreColor = score >= 80 ? 'text-green-600 bg-green-50' : score >= 60 ? 'text-yellow-600 bg-yellow-50' : 'text-slate-600 bg-slate-50';

  return (
    <div className="bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer">
      <div onClick={handleClick}>
        {/* Header */}
        <div className="h-28 bg-gradient-to-br from-slate-50 to-blue-50 rounded-t-xl flex items-center justify-center relative">
          <div className="text-3xl font-bold text-blue-200">{product.charAt(0)}</div>
          <span className={`absolute top-2 right-2 text-xs font-bold px-2 py-1 rounded-full ${scoreColor}`}>
            {score.toFixed(0)}
          </span>
        </div>

        <div className="p-3">
          {contextLabel && (
            <span className="text-xs text-blue-600 font-medium">{contextLabel}</span>
          )}
          <h4 className="font-semibold text-sm text-slate-800 mt-1 leading-snug">{product}</h4>
          {info.category && <p className="text-xs text-slate-400">{info.category}</p>}
          {info.price && (
            <p className="text-sm font-bold text-slate-700 mt-1">₹{info.price.toLocaleString('en-IN')}</p>
          )}
        </div>
      </div>

      {/* Reasons */}
      {reasons && reasons.length > 0 && (
        <div className="px-3 pb-1">
          <button
            onClick={() => setShowReasons(!showReasons)}
            className="text-xs text-blue-500 flex items-center gap-1 hover:text-blue-700"
          >
            Why recommended? {showReasons ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          {showReasons && (
            <ul className="mt-1 space-y-0.5">
              {reasons.slice(0, 3).map((r, i) => (
                <li key={i} className="text-xs text-slate-600 flex items-start gap-1">
                  <CheckCircle className="w-3 h-3 text-green-500 mt-0.5 flex-shrink-0" />
                  {r}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Add to Cart */}
      <div className="p-3 pt-1">
        <button
          onClick={handleAddToCart}
          disabled={adding}
          className="w-full text-xs bg-blue-600 hover:bg-blue-700 text-white py-1.5 rounded-lg transition-colors flex items-center justify-center gap-1 disabled:opacity-50"
        >
          <ShoppingCart className="w-3 h-3" />
          {adding ? 'Adding...' : 'Add to Cart'}
        </button>
      </div>
    </div>
  );
}
