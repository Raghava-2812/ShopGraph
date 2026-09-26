import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, Search, User, LogOut, Package } from 'lucide-react';
import { useAuth } from '../context/AuthContext.jsx';
import { useCart } from '../context/CartContext.jsx';

export default function Navbar() {
  const { user, logout } = useAuth();
  const { cart } = useCart();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = React.useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 text-blue-600 font-bold text-xl">
            <span className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white text-sm font-bold">SG</span>
            ShopGraph
          </Link>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex-1 max-w-md mx-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search products..."
                className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-slate-50"
              />
            </div>
          </form>

          {/* Right Actions */}
          <div className="flex items-center gap-4">
            <Link to="/products" className="text-sm text-slate-600 hover:text-blue-600 hidden sm:block font-medium">
              Products
            </Link>
            
            {user ? (
              <>
                <Link to="/orders" className="hidden sm:flex items-center gap-1 text-sm text-slate-600 hover:text-blue-600">
                  <Package className="w-4 h-4" />
                  <span className="hidden md:block">Orders</span>
                </Link>
                <Link to="/profile" className="flex items-center gap-1 text-sm text-slate-600 hover:text-blue-600">
                  <User className="w-4 h-4" />
                  <span className="hidden md:block">{user.name.split(' ')[0]}</span>
                </Link>
                <button
                  onClick={() => { logout(); navigate('/'); }}
                  className="text-slate-400 hover:text-red-500"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </>
            ) : (
              <Link to="/login" className="text-sm font-medium text-blue-600 hover:text-blue-700">
                Login
              </Link>
            )}

            {user && (
              <Link to="/cart" className="relative">
                <ShoppingCart className="w-6 h-6 text-slate-600 hover:text-blue-600" />
                {cart.item_count > 0 && (
                  <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {cart.item_count}
                  </span>
                )}
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
