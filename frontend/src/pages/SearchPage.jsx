import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { productsAPI, eventsAPI, recommendationsAPI } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';
import RecommendationSection from '../components/RecommendationSection.jsx';
import { Search } from 'lucide-react';

export default function SearchPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const query = params.get('q') || '';

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchInput, setSearchInput] = useState(query);
  const [recs, setRecs] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    setSearchInput(query);
    if (!query) return;

    setLoading(true);
    // Record SEARCH event
    eventsAPI.record('SEARCH_PRODUCT', null, query);

    productsAPI
      .search(query)
      .then((data) => {
        setResults(data);
        // If results exist, fetch recommendations for the top match
        if (data && data.length > 0) {
          setLoadingRecs(true);
          recommendationsAPI
            .forProduct(data[0].name, 4)
            .then((r) => {
              setRecs(r.related_products || r.recommendations || []);
            })
            .catch(console.error)
            .finally(() => setLoadingRecs(false));
        } else {
          // If no direct results, fall back to personalized/trending recs
          setLoadingRecs(true);
          recommendationsAPI
            .personalized(4)
            .then((r) => setRecs(r.recommendations || []))
            .catch(console.error)
            .finally(() => setLoadingRecs(false));
        }
      })
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
      {/* Search Input Box */}
      <form onSubmit={handleSearch} className="mb-8">
        <div className="relative max-w-xl">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search laptops, mice, audio, hardware..."
            className="w-full pl-12 pr-4 py-3 border border-slate-200 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          />
          <button
            type="submit"
            className="absolute right-2.5 top-1/2 -translate-y-1/2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-1.5 rounded-xl text-xs font-bold transition-colors shadow-sm"
          >
            Search
          </button>
        </div>
      </form>

      {query && (
        <p className="text-slate-500 text-sm mb-6">
          {loading ? 'Searching Knowledge Graph...' : `${results.length} results found for "${query}"`}
        </p>
      )}

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-slate-200 h-64 animate-pulse" />
          ))}
        </div>
      ) : results.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          {results.map((p) => (
            <ProductCard key={p.name} product={p} />
          ))}
        </div>
      ) : query ? (
        <div className="text-center py-16 text-slate-400 bg-white rounded-3xl border border-slate-200 p-8 shadow-sm">
          <Search className="w-12 h-12 mx-auto mb-3 opacity-30 text-blue-500" />
          <h3 className="text-base font-bold text-slate-700">No exact matches found for "{query}"</h3>
          <p className="text-xs text-slate-400 mt-1">Try broader terms like "laptop", "mouse", "monitor", or "dell".</p>
        </div>
      ) : (
        <div className="text-center py-16 text-slate-400">
          <p className="text-sm font-medium">Type keywords above to search products</p>
        </div>
      )}

      {/* Dynamic Recommendation Section on Search */}
      {recs && recs.length > 0 && (
        <div className="mt-14 pt-8 border-t border-slate-200">
          <RecommendationSection
            title="✨ You May Also Like"
            recommendations={recs}
            loading={loadingRecs}
            contextLabel="Related Recommendation"
          />
        </div>
      )}
    </div>
  );
}
