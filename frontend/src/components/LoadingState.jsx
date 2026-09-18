import React from 'react';
import { Loader2, Share2 } from 'lucide-react';

export default function LoadingState({ message = 'Finding products from the knowledge graph...' }) {
  return (
    <div className="my-12 py-16 px-6 bg-white rounded-2xl border border-slate-200/80 shadow-xs flex flex-col items-center justify-center text-center">
      <div className="relative mb-5">
        <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center">
          <Share2 className="w-8 h-8 text-blue-600 animate-pulse" />
        </div>
        <div className="absolute -bottom-1 -right-1 bg-white rounded-full p-1 shadow-sm">
          <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
        </div>
      </div>

      <h3 className="text-lg font-semibold text-slate-800">{message}</h3>
      <p className="text-xs text-slate-500 max-w-md mt-1.5 leading-relaxed">
        Traversing Neo4j relationship paths across categories, features, direct compatibility, and use cases...
      </p>

      {/* Skeleton cards */}
      <div className="w-full max-w-4xl grid grid-cols-1 sm:grid-cols-3 gap-4 mt-8 opacity-60">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-44 rounded-xl bg-slate-100 border border-slate-200 animate-pulse p-4 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="h-4 bg-slate-200 rounded w-3/4"></div>
              <div className="h-3 bg-slate-200 rounded w-1/2"></div>
            </div>
            <div className="space-y-1.5">
              <div className="h-2.5 bg-slate-200 rounded w-full"></div>
              <div className="h-2.5 bg-slate-200 rounded w-4/5"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
