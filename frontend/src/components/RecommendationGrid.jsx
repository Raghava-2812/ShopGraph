import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import RecommendationCard from './RecommendationCard.jsx';

export default function RecommendationGrid({
  purchasedProduct,
  recommendations = [],
  onViewExplanation,
  onProductClick,
}) {
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <section className="mt-8 sm:mt-12">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2 pb-5 border-b border-slate-200 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center justify-center p-1 rounded-md bg-blue-100 text-blue-700">
              <Sparkles className="w-4 h-4" />
            </span>
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-700">
              Personalized Recommendations
            </span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900 mt-1">
            Recommendations for <span className="text-blue-600 font-extrabold">{purchasedProduct}</span>
          </h2>
        </div>
        <p className="text-xs text-slate-500 font-medium">
          Showing <span className="font-semibold text-slate-700">{recommendations.length}</span> graph-ranked matches
        </p>
      </div>

      {/* Grid: 1 col on mobile, 2 on tablet, 3 on desktop */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {recommendations.map((item, index) => (
          <RecommendationCard
            key={item.product || index}
            product={item.product}
            score={item.score}
            reasons={item.reasons}
            onViewExplanation={onViewExplanation}
            onProductClick={onProductClick}
          />
        ))}
      </div>
    </section>
  );
}
