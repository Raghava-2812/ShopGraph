import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { productsAPI, recommendationsAPI } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';
import RecommendationSection from '../components/RecommendationSection.jsx';
import { SlidersHorizontal, Filter, ArrowUpDown, X } from 'lucide-react';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [sortBy, setSortBy] = useState('popular');
  const [loading, setLoading] = useState(true);

  const [categoryRecs, setCategoryRecs] = useState(null);
  const [loadingCategoryRecs, setLoadingCategoryRecs] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const initialCategory = params.get('category') || '';

  useEffect(() => {
    setSelectedCategory(initialCategory);
  }, [initialCategory]);

  useEffect(() => {
    productsAPI.categories().then(setCategories).catch(console.error);
    productsAPI.brands().then(setBrands).catch(console.error);
  }, []);

  useEffect(() => {
    setLoading(true);
    productsAPI
      .list({
        category: selectedCategory || undefined,
        brand: selectedBrand || undefined,
        sort: sortBy,
      })
      .then(setProducts)
      .catch(console.error)
      .finally(() => setLoading(false));

    // If a category is selected, fetch category recommendations and accessories
    if (selectedCategory) {
      setLoadingCategoryRecs(true);
      recommendationsAPI
        .forCategory(selectedCategory, 4)
        .then(setCategoryRecs)
        .catch(console.error)
        .finally(() => setLoadingCategoryRecs(false));
    } else {
      setCategoryRecs(null);
    }
  }, [selectedCategory, selectedBrand, sortBy]);

  const handleCategoryChange = (cat) => {
    setSelectedCategory(cat);
    if (cat) {
      navigate(`/products?category=${encodeURIComponent(cat)}`, { replace: true });
    } else {
      navigate('/products', { replace: true });
    }
  };

  const clearAllFilters = () => {
    setSelectedCategory('');
    setSelectedBrand('');
    setSortBy('popular');
    navigate('/products', { replace: true });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Title & Filter Controls Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <SlidersHorizontal className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900">
              {selectedCategory ? `${selectedCategory}` : 'All Products Catalog'}
            </h1>
            <p className="text-xs text-slate-500 font-medium">
              Showing {products.length} {products.length === 1 ? 'product' : 'products'} from Knowledge Graph
            </p>
          </div>
        </div>

        {/* Filter Dropdowns and Sorting */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Brand Filter */}
          <div className="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-3 py-1.5 shadow-sm text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedBrand}
              onChange={(e) => setSelectedBrand(e.target.value)}
              className="bg-transparent font-medium text-slate-700 outline-none cursor-pointer"
            >
              <option value="">All Brands</option>
              {brands.map((b) => (
                <option key={b} value={b}>
                  {b}
                </option>
              ))}
            </select>
          </div>

          {/* Sort By */}
          <div className="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-3 py-1.5 shadow-sm text-xs">
            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent font-medium text-slate-700 outline-none cursor-pointer"
            >
              <option value="popular">Most Popular</option>
              <option value="rating">Highest Rated</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
            </select>
          </div>

          {(selectedCategory || selectedBrand) && (
            <button
              onClick={clearAllFilters}
              className="text-xs font-semibold text-rose-600 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 py-1.5 px-3 rounded-xl transition-colors flex items-center gap-1"
            >
              <X className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Category Pills Bar */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button
          onClick={() => handleCategoryChange('')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-sm ${
            !selectedCategory
              ? 'bg-blue-600 text-white shadow-blue-500/20'
              : 'bg-white text-slate-600 border border-slate-200 hover:border-blue-300'
          }`}
        >
          All Categories
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => handleCategoryChange(cat)}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold transition-all shadow-sm ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white shadow-blue-500/20'
                : 'bg-white text-slate-600 border border-slate-200 hover:border-blue-300 hover:text-blue-600'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Main Product Grid */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-slate-200 h-72 animate-pulse" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-20 bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
          <p className="text-base font-bold text-slate-700">No products match your filter criteria</p>
          <p className="text-xs text-slate-400 mt-1 mb-4">Try clearing filters to view all products.</p>
          <button
            onClick={clearAllFilters}
            className="text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 px-4 py-2 rounded-xl transition-colors"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          {products.map((p) => (
            <ProductCard key={p.name} product={p} />
          ))}
        </div>
      )}

      {/* Category Add-on Recommendations (Section 19 requirement) */}
      {selectedCategory && categoryRecs && (
        <div className="mt-16 pt-8 border-t border-slate-200 space-y-10">
          {categoryRecs.popular_accessories?.length > 0 && (
            <div className="bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm">
              <h2 className="text-xl font-bold text-slate-800 mb-1 flex items-center gap-2">
                <span>🎒 Popular Add-ons & Accessories For {selectedCategory}</span>
              </h2>
              <p className="text-xs text-slate-500 mb-6">
                Hardware gear verified compatible with {selectedCategory} by the Knowledge Graph
              </p>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {categoryRecs.popular_accessories.map((p) => (
                  <ProductCard key={p.name} product={p} reason={`Compatible with ${selectedCategory}`} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
