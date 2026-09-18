import React from 'react';
import { HelpCircle, Check, Info } from 'lucide-react';
import ScoreBadge from './ScoreBadge.jsx';

export default function RecommendationCard({
  product,
  score,
  reasons = [],
  onViewExplanation,
  onProductClick,
}) {
  // Helper to get friendly badge styling for reason types
  const getReasonBadgeStyle = (reason) => {
    const text = reason.toLowerCase();
    if (text.includes('compatible') || text.includes('accessory') || text.includes('works with')) {
      return 'bg-emerald-50 text-emerald-800 border-emerald-200';
    }
    if (text.includes('shares') || text.includes('feature')) {
      return 'bg-blue-50 text-blue-800 border-blue-200';
    }
    if (text.includes('useful for') || text.includes('use case')) {
      return 'bg-purple-50 text-purple-800 border-purple-200';
    }
    if (text.includes('similar')) {
      return 'bg-indigo-50 text-indigo-800 border-indigo-200';
    }
    return 'bg-slate-50 text-slate-700 border-slate-200';
  };

  return (
    <div className="group bg-white rounded-2xl border border-slate-200/90 shadow-sm hover:shadow-md hover:border-blue-300 transition-all duration-200 flex flex-col justify-between p-5 relative overflow-hidden">
      {/* Top highlight bar */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity" />

      {/* Top Header: Title & Score */}
      <div>
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <h3
              onClick={() => onProductClick && onProductClick(product)}
              className="text-lg font-bold text-slate-900 group-hover:text-blue-600 transition-colors cursor-pointer line-clamp-2"
              title="Click to view product details"
            >
              {product}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1">
              <span>Graph Recommended</span>
              {onProductClick && (
                <button
                  type="button"
                  onClick={() => onProductClick(product)}
                  className="hover:underline text-blue-600 inline-flex items-center gap-0.5 ml-1"
                >
                  <Info className="w-3 h-3" /> details
                </button>
              )}
            </p>
          </div>

          <div className="shrink-0">
            <ScoreBadge score={score} />
          </div>
        </div>

        {/* Reasons / Knowledge Graph Evidence Chips */}
        <div className="mt-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Why It Matches
          </p>
          <ul className="space-y-1.5">
            {reasons.slice(0, 4).map((reason, idx) => (
              <li
                key={idx}
                className={`text-xs px-2.5 py-1 rounded-lg border flex items-center gap-2 ${getReasonBadgeStyle(reason)}`}
              >
                <Check className="w-3.5 h-3.5 shrink-0 text-current opacity-80" />
                <span className="truncate font-medium">{reason}</span>
              </li>
            ))}
            {reasons.length > 4 && (
              <li className="text-[11px] text-slate-500 pl-1">
                + {reasons.length - 4} more graph evidence points
              </li>
            )}
          </ul>
        </div>
      </div>

      {/* Action Footer */}
      <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between">
        <button
          type="button"
          onClick={() => onViewExplanation({ product, score, reasons })}
          className="w-full inline-flex items-center justify-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200/80 transition-colors"
        >
          <HelpCircle className="w-3.5 h-3.5" />
          <span>Why recommended?</span>
        </button>
      </div>
    </div>
  );
}
