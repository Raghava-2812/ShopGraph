import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Package } from 'lucide-react';
import { ordersAPI } from '../services/api.js';
import { useCart } from '../context/CartContext.jsx';
import { useAuth } from '../context/AuthContext.jsx';

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { cart, fetchCart, clearCart } = useCart();
  const [form, setForm] = useState({ name: '', address: '', city: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    if (user) { fetchCart(); setForm(f => ({ ...f, name: user.name })); }
    else navigate('/login');
  }, [user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.address || !form.city) {
      setError('Please fill in all shipping details');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await ordersAPI.create({ name: form.name, address: form.address, city: form.city });
      setSuccess(result);
      clearCart();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to place order. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="max-w-lg mx-auto px-4 py-16 text-center">
        <div className="bg-green-50 rounded-2xl p-8 border border-green-200">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Order Placed!</h2>
          <p className="text-slate-600 mb-2">Thank you for your purchase</p>
          <div className="bg-white rounded-xl p-4 border border-green-100 mb-6">
            <p className="text-sm text-slate-500">Order ID</p>
            <p className="text-xl font-bold text-green-600">{success.order_id}</p>
            <p className="text-sm text-slate-500 mt-1">Total: ₹{success.total_amount?.toLocaleString('en-IN')}</p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => navigate('/')} className="flex-1 border border-slate-200 text-slate-600 py-2 rounded-lg text-sm">Home</button>
            <button onClick={() => navigate('/orders')} className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium">My Orders</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-slate-800 mb-8">Checkout</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Shipping Form */}
        <div>
          <h2 className="font-bold text-slate-700 mb-4">Shipping Information</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Full Name</label>
              <input
                type="text" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                className="w-full border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your full name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Address</label>
              <input
                type="text" value={form.address} onChange={e => setForm(f => ({ ...f, address: e.target.value }))}
                className="w-full border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Street address"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">City</label>
              <input
                type="text" value={form.city} onChange={e => setForm(f => ({ ...f, city: e.target.value }))}
                className="w-full border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="City"
              />
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button
              type="submit" disabled={loading || cart.items.length === 0}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-semibold transition-colors disabled:opacity-50"
            >
              {loading ? 'Placing Order...' : `Place Order — ₹${cart.total.toLocaleString('en-IN')}`}
            </button>
          </form>
        </div>

        {/* Order Summary */}
        <div>
          <h2 className="font-bold text-slate-700 mb-4">Order Summary</h2>
          <div className="bg-slate-50 rounded-xl p-4 space-y-3">
            {cart.items.map(item => (
              <div key={item.id} className="flex justify-between text-sm">
                <span className="text-slate-700">{item.product_name} × {item.quantity}</span>
                {item.price && <span className="font-medium">₹{(item.price * item.quantity).toLocaleString('en-IN')}</span>}
              </div>
            ))}
            <div className="border-t border-slate-200 pt-3 flex justify-between font-bold">
              <span>Total</span>
              <span>₹{cart.total.toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
