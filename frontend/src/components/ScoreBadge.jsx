import React from 'react';

/**
 * ScoreBadge displays the transparent Knowledge Graph recommendation score (0-100).
 * Never framed as a probability, but explicitly as a Recommendation Score.
 */
export default function ScoreBadge({ score, size = 'default' }) {
  const numericScore = typeof score === 'number' ? score : parseFloat(score) || 0;
  const formattedScore = numericScore.toFixed(1);

  // Styling based on score ranges
  let colorClasses = {
    badge: 'bg-blue-50 text-blue-800 border-blue-200',
    number: 'text-blue-700',
    label: 'text-blue-600',
    ring: 'border-blue-300 bg-blue-500',
  };

  if (numericScore >= 85) {
    colorClasses = {
      badge: 'bg-emerald-50 text-emerald-900 border-emerald-200',
      number: 'text-emerald-700',
      label: 'text-emerald-600',
      ring: 'border-emerald-300 bg-emerald-500',
    };
  } else if (numericScore >= 70) {
    colorClasses = {
      badge: 'bg-blue-50 text-blue-900 border-blue-200',
      number: 'text-blue-700',
      label: 'text-blue-600',
      ring: 'border-blue-300 bg-blue-500',
    };
  } else if (numericScore >= 50) {
    colorClasses = {
      badge: 'bg-indigo-50 text-indigo-900 border-indigo-200',
      number: 'text-indigo-700',
      label: 'text-indigo-600',
      ring: 'border-indigo-300 bg-indigo-500',
    };
  } else {
    colorClasses = {
      badge: 'bg-slate-50 text-slate-800 border-slate-200',
      number: 'text-slate-700',
      label: 'text-slate-500',
      ring: 'border-slate-300 bg-slate-400',
    };
  }

  if (size === 'large') {
    return (
      <div className={`inline-flex flex-col items-center justify-center p-3.5 rounded-xl border ${colorClasses.badge} shadow-sm`}>
        <div className="flex items-baseline gap-1">
          <span className={`text-3xl font-extrabold tracking-tight ${colorClasses.number}`}>
            {formattedScore}
          </span>
          <span className="text-xs font-semibold text-slate-500">/100</span>
        </div>
        <span className={`text-[11px] font-bold uppercase tracking-wider mt-0.5 ${colorClasses.label}`}>
          Recommendation Score
        </span>
      </div>
    );
  }

  return (
    <div className={`flex flex-col items-center px-3 py-1.5 rounded-lg border ${colorClasses.badge} shadow-xs text-center min-w-[76px]`}>
      <span className={`text-lg font-bold leading-tight ${colorClasses.number}`}>
        {formattedScore}
      </span>
      <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500 leading-none mt-0.5">
        Match Score
      </span>
    </div>
  );
}
