import React from 'react';
import RecommendationCard from './RecommendationCard.jsx';

export default function RecommendationSection({ title, recommendations, loading, emptyMessage, contextLabel }) {
  if (loading) {
    return (
      <div className="mt-8">
        <h2 className="text-lg font-bold text-slate-800 mb-4">{title}</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => (
            <div key={i} className="bg-white rounded-xl border border-slate-200 h-52 animate-pulse">
              <div className="h-28 bg-slate-100 rounded-t-xl" />
              <div className="p-3 space-y-2">
                <div className="h-3 bg-slate-100 rounded" />
                <div className="h-3 bg-slate-100 rounded w-2/3" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    if (emptyMessage === null) return null;
    return null;
  }

  return (
    <div className="mt-8">
      <h2 className="text-lg font-bold text-slate-800 mb-4">{title}</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {recommendations.map((rec, i) => (
          <RecommendationCard key={rec.product || i} rec={rec} contextLabel={contextLabel} />
        ))}
      </div>
    </div>
  );
}
