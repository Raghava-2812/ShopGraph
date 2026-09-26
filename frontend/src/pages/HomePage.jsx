import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { productsAPI, recommendationsAPI } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';
import RecommendationSection from '../components/RecommendationSection.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { Search, TrendingUp, Star } from 'lucide-react';

export default function HomePage() {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [personalized, setPersonalized] = useState(null);
  const [loadingProducts, setLoadingProducts] = useState(true);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    productsAPI.list().then(setProducts).catch(console.error).finally(() => setLoadingProducts(false));
  }, []);

  useEffect(() => {
    setLoadingRecs(true);
    recommendationsAPI.personalized(8)
      .then(setPersonalized)
      .catch(console.error)
      .finally(() => setLoadingRecs(false));
  }, [user]);

  const featured = products.slice(0, 8);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-16 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl font-bold mb-4">ShopGraph</h1>
          <p className="text-blue-100 text-lg mb-8">
            Knowledge Graph-powered recommendations that understand what you need
          </p>
          <Link
            to="/products"
            className="bg-white text-blue-600 font-semibold px-8 py-3 rounded-xl hover:bg-blue-50 transition-colors inline-block"
          >
            Browse Products
          </Link>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Personalized Recommendations */}
        {user ? (
          <RecommendationSection
            title={personalized?.personalized ? '✨ Recommended for You' : '🔥 Featured Products'}
            recommendations={personalized?.recommendations}
            loading={loadingRecs}
          />
        ) : (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center mb-8">
            <Star className="w-8 h-8 text-blue-400 mx-auto mb-2" />
            <h3 className="font-semibold text-slate-700 mb-1">Get Personalized Recommendations</h3>
            <p className="text-sm text-slate-500 mb-4">Login to see recommendations based on your browsing and purchase history</p>
            <Link to="/login" className="bg-blue-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">
              Login
            </Link>
          </div>
        )}

        {/* Product Catalog */}
        <div className="mt-10">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              Popular Products
            </h2>
            <Link to="/products" className="text-sm text-blue-600 hover:underline font-medium">View all →</Link>
          </div>

          {loadingProducts ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {[1,2,3,4,5,6,7,8].map(i => (
                <div key={i} className="bg-white rounded-xl border border-slate-200 h-52 animate-pulse">
                  <div className="h-32 bg-slate-100 rounded-t-xl" />
                  <div className="p-4 space-y-2">
                    <div className="h-3 bg-slate-100 rounded" />
                    <div className="h-3 bg-slate-100 rounded w-2/3" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {featured.map(p => <ProductCard key={p.name} product={p} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
