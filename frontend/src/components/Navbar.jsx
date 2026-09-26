import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, Search, User, LogOut, Package, Heart, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { useCart } from '../context/CartContext.jsx';
import { useWishlist } from '../context/WishlistContext.jsx';

export default function Navbar() {
  const { user, logout } = useAuth();
  const { cart } = useCart();
  const { wishlistCount } = useWishlist();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm backdrop-blur-md bg-white/95">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5 text-blue-600 font-extrabold text-xl tracking-tight flex-shrink-0">
            <span className="w-9 h-9 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center text-white text-sm font-black shadow-md shadow-blue-500/20">
              SG
            </span>
            <span className="hidden sm:inline bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              ShopGraph
            </span>
          </Link>

          {/* Search Bar with auto-submit */}
          <form onSubmit={handleSearch} className="flex-1 max-w-lg">
            <div className="relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search 80+ products across 19 categories..."
                className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-slate-50 hover:bg-slate-100/70 transition-colors"
              />
            </div>
          </form>

          {/* Nav Links & Actions */}
          <div className="flex items-center gap-3 sm:gap-5 flex-shrink-0">
            <Link
              to="/products"
              className="text-sm font-medium text-slate-700 hover:text-blue-600 hidden md:block transition-colors"
            >
              All Products
            </Link>

            {/* Wishlist Link with Badge */}
            {user && (
              <Link
                to="/wishlist"
                className="relative p-2 text-slate-600 hover:text-rose-600 transition-colors rounded-xl hover:bg-slate-100"
                title="Wishlist"
              >
                <Heart className="w-5 h-5" />
                {wishlistCount > 0 && (
                  <span className="absolute top-1 right-1 bg-rose-500 text-white text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center shadow-sm">
                    {wishlistCount}
                  </span>
                )}
              </Link>
            )}

            {/* Cart Link with Badge */}
            {user && (
              <Link
                to="/cart"
                className="relative p-2 text-slate-600 hover:text-blue-600 transition-colors rounded-xl hover:bg-slate-100"
                title="Cart"
              >
                <ShoppingCart className="w-5 h-5" />
                {cart.item_count > 0 && (
                  <span className="absolute top-1 right-1 bg-blue-600 text-white text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center shadow-sm">
                    {cart.item_count}
                  </span>
                )}
              </Link>
            )}

            {/* Auth Actions */}
            {user ? (
              <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
                <Link
                  to="/orders"
                  className="hidden sm:flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-blue-600 py-1.5 px-2.5 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  <Package className="w-3.5 h-3.5" />
                  <span>Orders</span>
                </Link>

                <Link
                  to="/profile"
                  className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 bg-slate-100 py-1.5 px-3 rounded-lg hover:bg-slate-200 transition-colors"
                >
                  <User className="w-3.5 h-3.5 text-blue-600" />
                  <span className="max-w-[80px] truncate">{user.name.split(' ')[0]}</span>
                </Link>

                <button
                  onClick={() => {
                    logout();
                    navigate('/');
                  }}
                  className="p-1.5 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="text-xs font-semibold text-slate-700 hover:text-blue-600 py-2 px-3 rounded-lg hover:bg-slate-100 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="text-xs font-semibold bg-blue-600 text-white py-2 px-3.5 rounded-xl hover:bg-blue-700 transition-colors shadow-sm"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
