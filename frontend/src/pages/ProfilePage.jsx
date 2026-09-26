import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Package, LogOut, ShoppingCart } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) {
    return (
      <div className="max-w-lg mx-auto px-4 py-16 text-center">
        <p className="text-slate-500">Please <Link to="/login" className="text-blue-600">login</Link> to view your profile</p>
      </div>
    );
  }

  const handleLogout = () => { logout(); navigate('/'); };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-2xl font-bold text-slate-800 mb-6">Profile</h1>
      
      <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-blue-500" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-800">{user.name}</h2>
            <p className="text-slate-500">{user.email}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <Link to="/orders" className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4 hover:border-blue-300 transition-colors">
          <Package className="w-5 h-5 text-blue-500" />
          <div>
            <p className="font-medium text-slate-700">My Orders</p>
            <p className="text-xs text-slate-400">View order history</p>
          </div>
        </Link>
        <Link to="/cart" className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-4 hover:border-blue-300 transition-colors">
          <ShoppingCart className="w-5 h-5 text-blue-500" />
          <div>
            <p className="font-medium text-slate-700">Shopping Cart</p>
            <p className="text-xs text-slate-400">View your cart</p>
          </div>
        </Link>
        <button onClick={handleLogout} className="bg-white rounded-xl border border-red-100 p-4 flex items-center gap-4 hover:border-red-300 transition-colors text-left">
          <LogOut className="w-5 h-5 text-red-400" />
          <div>
            <p className="font-medium text-red-500">Logout</p>
            <p className="text-xs text-slate-400">Sign out of your account</p>
          </div>
        </button>
      </div>
    </div>
  );
}
