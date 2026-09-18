import React from 'react';
import { PackageSearch, ArrowUp } from 'lucide-react';

export default function EmptyState() {
  return (
    <div className="my-10 py-16 px-6 bg-white rounded-2xl border border-dashed border-slate-300 text-center flex flex-col items-center justify-center">
      <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center text-slate-400 mb-4">
        <PackageSearch className="w-8 h-8 text-slate-400" />
      </div>

      <h3 className="text-lg font-bold text-slate-800">
        Choose a product above
      </h3>
      <p className="text-sm text-slate-500 max-w-md mt-1.5 leading-relaxed">
        Select something you have purchased to discover related products.
      </p>

      <div className="mt-5 inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full border border-blue-100">
        <ArrowUp className="w-3.5 h-3.5" />
        <span>Pick a product from the dropdown and click "Get Recommendations"</span>
      </div>
    </div>
  );
}
