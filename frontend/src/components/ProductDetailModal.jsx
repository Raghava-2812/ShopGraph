import React from 'react';
import { X, Tag, Cpu, Briefcase, CheckCircle, Package, Layers, Info } from 'lucide-react';

export default function ProductDetailModal({
  isOpen,
  onClose,
  productDetails,
  loading = false,
  onSelectAsPurchased,
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6 animate-fadeIn">
      <div 
        className="relative bg-white rounded-2xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-100 flex items-start justify-between bg-slate-50/80">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600">
              Product Graph Node
            </span>
            <h3 className="text-xl font-bold text-slate-900 leading-tight">
              {loading ? 'Loading product details...' : productDetails?.name}
            </h3>
            {productDetails?.price && (
              <p className="text-sm font-semibold text-slate-700 mt-0.5">
                ₹{productDetails.price.toLocaleString()}
              </p>
            )}
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          {loading ? (
            <div className="py-12 text-center text-slate-500">
              <div className="inline-block w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
              <p className="text-sm">Fetching product attributes from Neo4j...</p>
            </div>
          ) : productDetails ? (
            <>
              {/* Category & Brand */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                    Category
                  </span>
                  <div className="flex items-center gap-1.5 font-bold text-slate-800 text-sm">
                    <Layers className="w-4 h-4 text-blue-600" />
                    <span>{productDetails.category || 'Unspecified'}</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                    Brand
                  </span>
                  <div className="flex items-center gap-1.5 font-bold text-slate-800 text-sm">
                    <Tag className="w-4 h-4 text-indigo-600" />
                    <span>{productDetails.brand || 'Unspecified'}</span>
                  </div>
                </div>
              </div>

              {productDetails.description && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">
                    Description
                  </h4>
                  <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-200/80">
                    {productDetails.description}
                  </p>
                </div>
              )}

              {/* Features */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                  <Cpu className="w-3.5 h-3.5 text-blue-600" />
                  <span>Hardware & Specs Features</span>
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {productDetails.features && productDetails.features.length > 0 ? (
                    productDetails.features.map((f, i) => (
                      <span key={i} className="text-xs font-medium px-2.5 py-1 bg-blue-50 text-blue-800 rounded-lg border border-blue-200">
                        {f}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400">None listed</span>
                  )}
                </div>
              </div>

              {/* Use Cases */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-purple-600" />
                  <span>Use Cases & Workflows</span>
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {productDetails.use_cases && productDetails.use_cases.length > 0 ? (
                    productDetails.use_cases.map((u, i) => (
                      <span key={i} className="text-xs font-medium px-2.5 py-1 bg-purple-50 text-purple-800 rounded-lg border border-purple-200">
                        {u}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400">None listed</span>
                  )}
                </div>
              </div>

              {/* Compatible Products */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Compatible Products</span>
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {productDetails.compatible_with && productDetails.compatible_with.length > 0 ? (
                    productDetails.compatible_with.map((c, i) => (
                      <span key={i} className="text-xs font-medium px-2.5 py-1 bg-emerald-50 text-emerald-800 rounded-lg border border-emerald-200">
                        {c}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400">No direct compatibility links</span>
                  )}
                </div>
              </div>

              {/* Accessories */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1.5">
                  <Package className="w-3.5 h-3.5 text-amber-600" />
                  <span>Accessories</span>
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {productDetails.accessories && productDetails.accessories.length > 0 ? (
                    productDetails.accessories.map((a, i) => (
                      <span key={i} className="text-xs font-medium px-2.5 py-1 bg-amber-50 text-amber-800 rounded-lg border border-amber-200">
                        {a}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-400">No accessories linked</span>
                  )}
                </div>
              </div>
            </>
          ) : (
            <p className="text-sm text-slate-500">No details found for this product.</p>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          {productDetails && onSelectAsPurchased && (
            <button
              type="button"
              onClick={() => {
                onSelectAsPurchased(productDetails.name);
                onClose();
              }}
              className="text-xs font-bold text-blue-600 hover:text-blue-800 hover:underline"
            >
              Set as purchased product
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            className="ml-auto px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 hover:bg-slate-800 text-white transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
