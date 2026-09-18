import React from 'react';
import { X, Network, CheckCircle2, ShieldCheck, ArrowRight, Share2, Sparkles } from 'lucide-react';
import ScoreBadge from './ScoreBadge.jsx';

export default function ExplanationPanel({
  isOpen,
  onClose,
  purchasedProduct,
  recommendation,
}) {
  if (!isOpen || !recommendation) return null;

  const { product, score, reasons = [] } = recommendation;

  // Extract structured reasoning from backend strings
  const directRelationships = [];
  const sharedFeatures = [];
  const useCases = [];
  const otherReasons = [];

  reasons.forEach((r) => {
    const text = r.toLowerCase();
    if (text.includes('compatible') || text.includes('accessory') || text.includes('works with') || text.includes('similar')) {
      directRelationships.push(r);
    } else if (text.includes('shares') || text.includes('feature')) {
      sharedFeatures.push(r);
    } else if (text.includes('useful for') || text.includes('use case')) {
      useCases.push(r);
    } else {
      otherReasons.push(r);
    }
  });

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6 animate-fadeIn">
      <div 
        className="relative bg-white rounded-2xl max-w-2xl w-full shadow-2xl border border-slate-200 overflow-hidden transform transition-all"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-5 border-b border-slate-100 flex items-start justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center shrink-0">
              <Network className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600">
                Knowledge Graph Evidence
              </span>
              <h3 className="text-xl font-bold text-slate-900 leading-tight">
                Why was <span className="text-blue-600">{product}</span> recommended?
              </h3>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
          {/* Score overview banner */}
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200/80">
            <div>
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Graph Traversal Score
              </span>
              <p className="text-sm font-medium text-slate-700 mt-0.5">
                Calculated across 5 relationship dimensions in Neo4j
              </p>
            </div>
            <ScoreBadge score={score} size="large" />
          </div>

          {/* Graph Path Visualization (ASCII / Visual Tree) */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Share2 className="w-4 h-4 text-blue-600" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Graph Traversal Path
              </h4>
            </div>

            <div className="p-4 bg-slate-900 text-slate-100 rounded-xl font-mono text-xs overflow-x-auto shadow-inner border border-slate-800 leading-relaxed">
              <div className="text-blue-400 font-bold mb-1">
                {purchasedProduct}
              </div>
              <div className="text-slate-400">│</div>
              
              {directRelationships.length > 0 && (
                <>
                  <div className="text-emerald-400">
                    ├── [DIRECT_RELATIONSHIP] ──► <span className="text-slate-100 font-bold">{product}</span>
                  </div>
                  <div className="text-slate-400">│</div>
                </>
              )}

              {sharedFeatures.length > 0 && (
                <>
                  <div className="text-blue-300">
                    ├── [HAS_FEATURE] ──────────► {sharedFeatures[0].replace(/Shares\s+/i, '').replace(/\s+feature.*$/i, '') || 'Shared Feature'}
                  </div>
                  <div className="text-slate-500 pl-4">
                    │                               ▲
                  </div>
                  <div className="text-slate-500 pl-4">
                    │                         [HAS_FEATURE]
                  </div>
                  <div className="text-slate-500 pl-4">
                    │                               │
                  </div>
                  <div className="text-blue-300">
                    └─── [SHARED_NODE] ─────────────► <span className="text-slate-100 font-bold">{product}</span>
                  </div>
                </>
              )}

              {sharedFeatures.length === 0 && directRelationships.length === 0 && (
                <div className="text-indigo-300">
                  └─── [GRAPH_EXPLORATION] ─────► <span className="text-slate-100 font-bold">{product}</span>
                </div>
              )}
            </div>
          </div>

          {/* Evidence Details */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Verified Graph Evidence ({reasons.length} points)
              </h4>
            </div>

            <ul className="space-y-2.5">
              {reasons.map((reason, idx) => (
                <li
                  key={idx}
                  className="flex items-start gap-2.5 p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 text-xs sm:text-sm text-slate-800"
                >
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span className="font-medium leading-relaxed">{reason}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Scoring Dimension Breakdown Note */}
          <div className="bg-blue-50/70 border border-blue-100 rounded-xl p-3.5 text-xs text-blue-900 leading-relaxed">
            <strong className="font-bold flex items-center gap-1.5 mb-1">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              Transparent Graph Scoring
            </strong>
            This score is composed of weighted signals: 40% Relationship Score, 25% Feature Overlap, 15% Category Alignment, 10% Use Case Synergy, and 10% Similarity.
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-sm font-semibold bg-slate-900 hover:bg-slate-800 text-white transition-colors"
          >
            Close Explanation
          </button>
        </div>
      </div>
    </div>
  );
}
