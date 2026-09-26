import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { productsAPI, eventsAPI } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';
import { Search } from 'lucide-react';

export default function SearchPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const query = params.get('q') || '';

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchInput, setSearchInput] = useState(query);

  useEffect(() => {
    if (!query) return;
    setLoading(true);
    // Record SEARCH event
    eventsAPI.record('SEARCH', null, query);
    productsAPI.search(query)
      .then(setResults)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [query]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchInput.trim())}`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <form onSubmit={handleSearch} className="mb-8">
        <div className="relative max-w-xl">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search products..."
            className="w-full pl-12 pr-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" className="absolute right-2 top-1/2 -translate-y-1/2 bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium">
            Search
          </button>
        </div>
      </form>

      {query && (
        <p className="text-slate-500 text-sm mb-6">
          {loading ? 'Searching...' : `${results.length} results for "${query}"`}
        </p>
      )}

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 h-52 animate-pulse">
              <div className="h-32 bg-slate-100 rounded-t-xl" />
            </div>
          ))}
        </div>
      ) : results.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {results.map(p => <ProductCard key={p.name} product={p} />)}
        </div>
      ) : query ? (
        <div className="text-center py-16 text-slate-400">
          <Search className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p>No products found for "{query}"</p>
        </div>
      ) : (
        <div className="text-center py-16 text-slate-400">
          <p>Type something to search</p>
        </div>
      )}
    </div>
  );
}
