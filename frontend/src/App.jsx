/**
 * ShopGraph - Main Application Component & Route Configuration
 * File: frontend/src/App.jsx
 *
 * Configures client-side routing via React Router DOM and wraps routes
 * inside top-level Context Providers (Auth, Cart, Wishlist).
 *
 * Provider hierarchy:
 *   BrowserRouter
 *     └─ AuthProvider       (Manages user authentication & JWT tokens)
 *          └─ CartProvider   (Manages cart line items, pricing & events)
 *               └─ WishlistProvider (Manages saved items & optimistic updates)
 *                    └─ Routes
 */

import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.jsx';
import { CartProvider } from './context/CartContext.jsx';
import { WishlistProvider } from './context/WishlistContext.jsx';
import Navbar from './components/Navbar.jsx';
import HomePage from './pages/HomePage.jsx';
import ProductsPage from './pages/ProductsPage.jsx';
import ProductDetailPage from './pages/ProductDetailPage.jsx';
import SearchPage from './pages/SearchPage.jsx';
import CartPage from './pages/CartPage.jsx';
import WishlistPage from './pages/WishlistPage.jsx';
import CheckoutPage from './pages/CheckoutPage.jsx';
import OrdersPage from './pages/OrdersPage.jsx';
import ProfilePage from './pages/ProfilePage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';

/**
 * Standard Application Shell Layout
 *
 * Provides a sticky navigation header, main content slot, and shared footer.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Route component to render in the main slot
 */
function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Global Navigation Bar */}
      <Navbar />

      {/* Primary Page Content */}
      <main>{children}</main>

      {/* Global Application Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-400">
          ShopGraph — Knowledge Graph Powered E-Commerce · Neo4j · FastAPI · React
        </div>
      </footer>
    </div>
  );
}

/**
 * Root Application Router Component
 */
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <WishlistProvider>
            <Routes>
              {/* Main Storefront Routes (wrapped in standard Layout) */}
              <Route path="/" element={<Layout><HomePage /></Layout>} />
              <Route path="/products" element={<Layout><ProductsPage /></Layout>} />
              <Route path="/products/:productName" element={<Layout><ProductDetailPage /></Layout>} />
              <Route path="/search" element={<Layout><SearchPage /></Layout>} />
              <Route path="/cart" element={<Layout><CartPage /></Layout>} />
              <Route path="/wishlist" element={<Layout><WishlistPage /></Layout>} />
              <Route path="/checkout" element={<Layout><CheckoutPage /></Layout>} />
              <Route path="/orders" element={<Layout><OrdersPage /></Layout>} />
              <Route path="/profile" element={<Layout><ProfilePage /></Layout>} />

              {/* Authentication Routes (clean minimal layout without Navbar) */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Routes>
          </WishlistProvider>
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
