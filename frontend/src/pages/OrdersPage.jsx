import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Package, Clock } from 'lucide-react';
import { ordersAPI } from '../services/api.js';
import { useAuth } from '../context/AuthContext.jsx';

export default function OrdersPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    ordersAPI.list()
      .then(setOrders)
      .catch(() => setError('Failed to load orders'))
      .finally(() => setLoading(false));
  }, [user]);

  if (loading) return (
    <div className="text-center py-16">
      <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-slate-800 mb-6 flex items-center gap-2">
        <Package className="w-6 h-6 text-blue-500" />
        My Orders
      </h1>

      {error ? (
        <p className="text-red-500">{error}</p>
      ) : orders.length === 0 ? (
        <div className="text-center py-16">
          <Package className="w-12 h-12 text-slate-200 mx-auto mb-4" />
          <p className="text-slate-400 mb-4">No orders yet</p>
          <Link to="/products" className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium">Shop Now</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map(order => (
            <div key={order.order_id} className="bg-white rounded-xl border border-slate-200 p-5">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <p className="font-bold text-slate-800">{order.order_id}</p>
                  <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                    <Clock className="w-3 h-3" />
                    {order.created_at ? new Date(order.created_at).toLocaleDateString('en-IN') : 'Unknown date'}
                  </p>
                </div>
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                  order.status === 'Delivered' ? 'bg-green-50 text-green-600' : 'bg-yellow-50 text-yellow-600'
                }`}>
                  {order.status}
                </span>
              </div>
              <div className="space-y-1">
                {order.items.map((item, i) => (
                  <div key={i} className="text-sm text-slate-600 flex justify-between">
                    <Link to={`/products/${encodeURIComponent(item.product_name)}`} className="hover:text-blue-600">
                      {item.product_name} × {item.quantity}
                    </Link>
                    {item.price && <span>₹{(item.price * item.quantity).toLocaleString('en-IN')}</span>}
                  </div>
                ))}
              </div>
              <div className="border-t border-slate-100 mt-3 pt-3 flex justify-between">
                <span className="text-sm text-slate-500">Total</span>
                <span className="font-bold text-slate-800">₹{order.total_amount?.toLocaleString('en-IN')}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
