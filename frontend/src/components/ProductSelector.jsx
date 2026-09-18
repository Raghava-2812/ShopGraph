import React from 'react';
import { ShoppingBag, Sparkles, ChevronDown, RefreshCw, SlidersHorizontal, Info } from 'lucide-react';

export default function ProductSelector({
  products = [],
  selectedProduct,
  onSelectProduct,
  onGetRecommendations,
  loading = false,
  topK = 5,
  onChangeTopK,
  onViewProductDetails,
  usingFallback = false,
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedProduct && !loading) {
      onGetRecommendations();
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-8">
      {/* Hero Header */}
      <div className="text-center max-w-2xl mx-auto mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold mb-3 border border-blue-200/60">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          <span>Neo4j Graph-Driven Engine</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
          Smart Recommendations <br className="hidden sm:block" />
          <span className="text-blue-600">Powered by Knowledge Graphs</span>
        </h1>
        <p className="text-sm sm:text-base text-slate-600 mt-3 leading-relaxed">
          Tell us what you purchased and discover products that fit your needs.
          Every recommendation is backed by relationships in the product knowledge graph.
        </p>

        {usingFallback && (
          <div className="mt-3 inline-block text-xs text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1 rounded-lg">
            ⚠️ Showing offline fallback catalog products. Ensure FastAPI backend is connected.
          </div>
        )}
      </div>

      {/* Selection Form */}
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
        <div className="flex flex-col gap-4">
          <label className="block text-sm font-bold text-slate-800">
            What did you purchase?
          </label>

          <div className="flex flex-col sm:flex-row gap-3">
            {/* Product Dropdown */}
            <div className="relative flex-1">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <ShoppingBag className="w-5 h-5" />
              </div>
              <select
                value={selectedProduct}
                onChange={(e) => onSelectProduct(e.target.value)}
                className="w-full pl-11 pr-10 py-3.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-800 text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all appearance-none cursor-pointer"
              >
                <option value="" disabled>
                  Select a product...
                </option>
                {products.map((p, idx) => {
                  const name = typeof p === 'string' ? p : p.name;
                  const category = typeof p === 'object' && p.category ? ` (${p.category})` : '';
                  return (
                    <option key={idx} value={name}>
                      {name}{category}
                    </option>
                  );
                })}
              </select>
              <div className="absolute inset-y-0 right-0 pr-3.5 flex items-center pointer-events-none text-slate-400">
                <ChevronDown className="w-4 h-4" />
              </div>
            </div>

            {/* Top-K Selector */}
            <div className="sm:w-36 shrink-0 relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <SlidersHorizontal className="w-4 h-4" />
              </div>
              <select
                value={topK}
                onChange={(e) => onChangeTopK && onChangeTopK(Number(e.target.value))}
                className="w-full pl-9 pr-8 py-3.5 bg-slate-50 border border-slate-300 rounded-xl text-slate-700 text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all appearance-none cursor-pointer"
                title="Number of recommendations"
              >
                <option value={3}>Top 3</option>
                <option value={5}>Top 5</option>
                <option value={10}>Top 10</option>
              </select>
              <div className="absolute inset-y-0 right-0 pr-2.5 flex items-center pointer-events-none text-slate-400">
                <ChevronDown className="w-3.5 h-3.5" />
              </div>
            </div>

            {/* Submit / Recommend Button */}
            <button
              type="submit"
              disabled={!selectedProduct || loading}
              className="sm:w-auto px-7 py-3.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white text-sm font-bold rounded-xl shadow-md shadow-blue-500/20 disabled:shadow-none transition-all flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed shrink-0 active:scale-[0.98]"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Analyzing Graph...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Get Recommendations</span>
                </>
              )}
            </button>
          </div>

          {/* Quick Details link for selected product */}
          {selectedProduct && onViewProductDetails && (
            <div className="flex items-center justify-between text-xs text-slate-500 pt-1 px-1">
              <span>Selected: <strong className="text-slate-800">{selectedProduct}</strong></span>
              <button
                type="button"
                onClick={() => onViewProductDetails(selectedProduct)}
                className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium hover:underline cursor-pointer"
              >
                <Info className="w-3.5 h-3.5" />
                <span>View Product Graph Details</span>
              </button>
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
