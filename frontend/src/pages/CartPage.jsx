import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Trash2, Plus, Minus, ShoppingCart } from 'lucide-react';
import { useCart } from '../context/CartContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { recommendationsAPI } from '../services/api.js';
import RecommendationSection from '../components/RecommendationSection.jsx';

export default function CartPage() {
  const { user } = useAuth();
  const { cart, fetchCart, removeFromCart, updateQuantity, loading } = useCart();
  const navigate = useNavigate();
  const [cartRecs, setCartRecs] = useState(null);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    if (user) fetchCart();
  }, [user]);

  useEffect(() => {
    if (cart.items.length === 0) { setCartRecs(null); return; }
    setLoadingRecs(true);
    recommendationsAPI.forCart()
      .then(setCartRecs)
      .catch(console.error)
      .finally(() => setLoadingRecs(false));
  }, [cart.items.length]);

  if (!user) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <ShoppingCart className="w-12 h-12 text-slate-300 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-slate-700 mb-2">Your Cart</h2>
        <p className="text-slate-500 mb-6">Please login to view your cart</p>
        <Link to="/login" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium">Login</Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
        <ShoppingCart className="w-6 h-6 text-blue-500" />
        Shopping Cart
      </h1>

      {cart.items.length === 0 ? (
        <div className="text-center py-16">
          <ShoppingCart className="w-12 h-12 text-slate-200 mx-auto mb-4" />
          <p className="text-slate-400 mb-4">Your cart is empty</p>
          <Link to="/products" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium text-sm">Browse Products</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-4">
            {cart.items.map(item => (
              <div key={item.id} className="bg-white rounded-xl border border-slate-200 p-4 flex gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span className="text-2xl font-bold text-blue-200">{item.product_name.charAt(0)}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <Link to={`/products/${encodeURIComponent(item.product_name)}`} className="font-semibold text-slate-800 hover:text-blue-600 text-sm">
                    {item.product_name}
                  </Link>
                  {item.price && (
                    <p className="text-slate-600 font-medium mt-0.5">₹{item.price.toLocaleString('en-IN')}</p>
                  )}
                  <div className="flex items-center gap-3 mt-2">
                    <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="w-7 h-7 rounded-full border border-slate-200 flex items-center justify-center hover:bg-slate-50">
                      <Minus className="w-3 h-3" />
                    </button>
                    <span className="text-sm font-medium w-6 text-center">{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="w-7 h-7 rounded-full border border-slate-200 flex items-center justify-center hover:bg-slate-50">
                      <Plus className="w-3 h-3" />
                    </button>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  {item.price && (
                    <span className="font-bold text-slate-800">₹{(item.price * item.quantity).toLocaleString('en-IN')}</span>
                  )}
                  <button onClick={() => removeFromCart(item.id, item.product_name)} className="text-red-400 hover:text-red-600">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary */}
          <div>
            <div className="bg-white rounded-xl border border-slate-200 p-6 sticky top-24">
              <h2 className="font-bold text-slate-800 mb-4">Order Summary</h2>
              <div className="space-y-2 text-sm text-slate-600">
                <div className="flex justify-between">
                  <span>Subtotal ({cart.item_count} items)</span>
                  <span>₹{cart.total.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between">
                  <span>Delivery</span>
                  <span className="text-green-600">Free</span>
                </div>
              </div>
              <div className="border-t border-slate-100 mt-4 pt-4 flex justify-between font-bold text-slate-800">
                <span>Total</span>
                <span>₹{cart.total.toLocaleString('en-IN')}</span>
              </div>
              <button
                onClick={() => navigate('/checkout')}
                className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-semibold transition-colors"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Cart Recommendations — Complete Your Setup */}
      {cart.items.length > 0 && (
        <RecommendationSection
          title="🛍️ Complete Your Setup"
          recommendations={cartRecs?.recommendations}
          loading={loadingRecs}
          emptyMessage={null}
          contextLabel="Pairs well with your cart"
        />
      )}
    </div>
  );
}
