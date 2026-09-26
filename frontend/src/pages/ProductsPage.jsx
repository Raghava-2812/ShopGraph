import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { productsAPI } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';
import { SlidersHorizontal } from 'lucide-react';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const initialCategory = params.get('category') || '';

  useEffect(() => {
    setSelectedCategory(initialCategory);
  }, [initialCategory]);

  useEffect(() => {
    productsAPI.categories().then(setCategories).catch(console.error);
  }, []);

  useEffect(() => {
    setLoading(true);
    productsAPI.list(selectedCategory || null)
      .then(setProducts)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedCategory]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-6">
        <SlidersHorizontal className="w-5 h-5 text-blue-500" />
        <h1 className="text-2xl font-bold text-slate-800">Product Catalog</h1>
        <span className="text-sm text-slate-400">({products.length} products)</span>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button
          onClick={() => setSelectedCategory('')}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
            !selectedCategory ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200 hover:border-blue-300'
          }`}
        >
          All
        </button>
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              selectedCategory === cat ? 'bg-blue-600 text-white' : 'bg-white text-slate-600 border border-slate-200 hover:border-blue-300'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading ? (
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
      ) : products.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <p className="text-lg font-medium">No products found</p>
          <button onClick={() => setSelectedCategory('')} className="mt-3 text-blue-600 text-sm">Clear filter</button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {products.map(p => <ProductCard key={p.name} product={p} />)}
        </div>
      )}
    </div>
  );
}
