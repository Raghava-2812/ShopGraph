import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { productsAPI, recommendationsAPI } from '../services/api.js';
import ProductCard from '../components/ProductCard.jsx';
import RecommendationCard from '../components/RecommendationCard.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import {
  Sparkles,
  TrendingUp,
  History,
  Target,
  ArrowRight,
  Layers,
  Zap,
  Laptop,
  Smartphone,
  Headphones,
  Monitor,
  Mouse,
  Tv,
} from 'lucide-react';

const CATEGORY_ICONS = {
  Laptops: '💻',
  'Gaming Laptops': '⚡',
  Monitors: '🖥️',
  Keyboards: '⌨️',
  Mice: '🖱️',
  Headphones: '🎧',
  Earbuds: '🎵',
  Smartphones: '📱',
  Tablets: '📲',
  'Smart Watches': '⌚',
  Webcams: '📷',
  Speakers: '🔊',
  'USB Hubs': '🔌',
  Storage: '💾',
  Backpacks: '🎒',
};

export default function HomePage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [categories, setCategories] = useState([]);
  const [trendingProducts, setTrendingProducts] = useState([]);
  const [personalizedData, setPersonalizedData] = useState(null);
  const [loadingRecs, setLoadingRecs] = useState(true);
  const [loadingProducts, setLoadingProducts] = useState(true);

  // Fetch categories & trending catalog products
  useEffect(() => {
    productsAPI.categories().then(setCategories).catch(console.error);

    productsAPI
      .list({ sort: 'popular' })
      .then((prods) => {
        setTrendingProducts(prods);
      })
      .catch(console.error)
      .finally(() => setLoadingProducts(false));
  }, []);

  // Fetch personalized recommendation payload
  const refreshRecommendations = () => {
    setLoadingRecs(true);
    recommendationsAPI
      .personalized(8)
      .then(setPersonalizedData)
      .catch(console.error)
      .finally(() => setLoadingRecs(false));
  };

  useEffect(() => {
    refreshRecommendations();
  }, [user]);

  const recommendedItems = personalizedData?.recommendations || [];
  const recentlyViewed = personalizedData?.recently_viewed || [];
  const relatedToInterests = personalizedData?.related_to_interests;
  const isPersonalized = personalizedData?.personalized;

  return (
    <div className="min-h-screen bg-slate-50/70 pb-16">
      {/* Hero Banner Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-blue-700 via-indigo-700 to-slate-900 text-white py-14 px-4 sm:px-6 lg:px-8 shadow-md">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:16px_16px]" />
        
        <div className="relative max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="max-w-2xl text-center md:text-left">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/10 backdrop-blur-md text-blue-200 border border-white/10 mb-4">
              <Sparkles className="w-3.5 h-3.5 text-amber-300" />
              Real-Time Graph Recommendation System
            </span>
            <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
              Smarter Shopping with Knowledge Graphs.
            </h1>
            <p className="mt-3 text-base sm:text-lg text-blue-100/90 leading-relaxed">
              Explore 80+ rich products with dynamic recommendations driven by compatibility,
              hardware specs, and your real-time browsing behavior.
            </p>

            <div className="mt-6 flex flex-wrap items-center justify-center md:justify-start gap-3">
              <Link
                to="/products"
                className="bg-white text-blue-700 font-bold px-6 py-2.5 rounded-xl hover:bg-blue-50 transition-all shadow-md active:scale-95 text-sm flex items-center gap-1.5"
              >
                <span>Browse 80+ Products</span>
                <ArrowRight className="w-4 h-4" />
              </Link>

              {!user && (
                <Link
                  to="/login"
                  className="bg-white/15 hover:bg-white/20 text-white font-semibold px-5 py-2.5 rounded-xl transition-all border border-white/20 text-sm"
                >
                  Login as Demo User
                </Link>
              )}
            </div>
          </div>

          {/* Graph Stats Card */}
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-5 w-full md:w-80 text-white/90 shadow-xl">
            <div className="text-xs font-semibold tracking-wider uppercase text-blue-200 mb-3 flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-amber-300" />
              Knowledge Graph Metrics
            </div>
            <div className="grid grid-cols-2 gap-3 text-center">
              <div className="bg-white/10 rounded-xl p-2.5">
                <div className="text-2xl font-black text-white">83</div>
                <div className="text-[11px] text-blue-200">Products</div>
              </div>
              <div className="bg-white/10 rounded-xl p-2.5">
                <div className="text-2xl font-black text-white">19</div>
                <div className="text-[11px] text-blue-200">Categories</div>
              </div>
              <div className="bg-white/10 rounded-xl p-2.5">
                <div className="text-2xl font-black text-white">26</div>
                <div className="text-[11px] text-blue-200">Brands</div>
              </div>
              <div className="bg-white/10 rounded-xl p-2.5">
                <div className="text-2xl font-black text-white">270+</div>
                <div className="text-[11px] text-blue-200">Relationships</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Category Navigation Pills */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-6">
        <div className="bg-white rounded-2xl border border-slate-200 shadow-md p-3 flex items-center gap-2 overflow-x-auto no-scrollbar">
          <Link
            to="/products"
            className="flex-shrink-0 px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 text-white hover:bg-blue-600 transition-colors"
          >
            All Products
          </Link>
          {categories.map((cat) => (
            <Link
              key={cat}
              to={`/products?category=${encodeURIComponent(cat)}`}
              className="flex-shrink-0 px-3.5 py-2 rounded-xl text-xs font-medium text-slate-700 bg-slate-100 hover:bg-blue-50 hover:text-blue-600 transition-all flex items-center gap-1.5"
            >
              <span>{CATEGORY_ICONS[cat] || '📦'}</span>
              <span>{cat}</span>
            </Link>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-10 space-y-12">
        {/* 1. Recommended For You (Personalized or Trending) */}
        <section>
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-800 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-indigo-600" />
                <span>{isPersonalized ? 'Recommended For You' : '🔥 Popular Trending Products'}</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                {isPersonalized
                  ? 'Real-time recommendations powered by graph traversal and your browsing signals'
                  : 'Top rated customer favorites across laptops, smartphones, audio and accessories'}
              </p>
            </div>
            <Link to="/products" className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1">
              <span>View catalog</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {loadingRecs ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-white rounded-2xl border border-slate-200 h-64 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {recommendedItems.slice(0, 8).map((rec, idx) => (
                <RecommendationCard key={rec.product || idx} rec={rec} />
              ))}
            </div>
          )}
        </section>

        {/* 2. Recently Viewed (User browsing history) */}
        {recentlyViewed && recentlyViewed.length > 0 && (
          <section className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
                <History className="w-5 h-5 text-blue-600" />
                <span>Recently Viewed</span>
              </h2>
              <span className="text-xs text-slate-400 font-medium">Updated in real-time</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {recentlyViewed.map((prod) => (
                <ProductCard key={prod.name} product={prod} />
              ))}
            </div>
          </section>
        )}

        {/* 3. Related To Your Interests (Dynamic category preference) */}
        {relatedToInterests && relatedToInterests.products?.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-5">
              <div>
                <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <Target className="w-5 h-5 text-emerald-600" />
                  <span>{relatedToInterests.title}</span>
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Curated picks based on your recent engagement with {relatedToInterests.category}
                </p>
              </div>
              <Link
                to={`/products?category=${encodeURIComponent(relatedToInterests.category)}`}
                className="text-xs font-semibold text-blue-600 hover:underline"
              >
                More in {relatedToInterests.category} →
              </Link>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
              {relatedToInterests.products.slice(0, 4).map((p) => (
                <ProductCard key={p.name} product={p} reason={`Top pick in ${relatedToInterests.category}`} />
              ))}
            </div>
          </section>
        )}

        {/* 4. Popular Laptops & Workstations */}
        <section>
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <Laptop className="w-5 h-5 text-blue-600" />
                <span>Top Laptops & Workstations</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                From ultra-portables to gaming powerhouses
              </p>
            </div>
            <Link to="/products?category=Laptops" className="text-xs font-semibold text-blue-600 hover:underline">
              See all laptops →
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {trendingProducts
              .filter((p) => p.category === 'Laptops' || p.category === 'Gaming Laptops')
              .slice(0, 4)
              .map((p) => (
                <ProductCard key={p.name} product={p} />
              ))}
          </div>
        </section>

        {/* 5. Essential Accessories & Audio */}
        <section>
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <Headphones className="w-5 h-5 text-purple-600" />
                <span>Accessories & Audio Essentials</span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Mice, keyboards, ANC headphones, and USB-C docks
              </p>
            </div>
            <Link to="/products" className="text-xs font-semibold text-blue-600 hover:underline">
              Explore gear →
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {trendingProducts
              .filter((p) =>
                ['Mice', 'Keyboards', 'Headphones', 'Earbuds', 'USB Hubs'].includes(p.category)
              )
              .slice(0, 4)
              .map((p) => (
                <ProductCard key={p.name} product={p} />
              ))}
          </div>
        </section>
      </div>
    </div>
  );
}
