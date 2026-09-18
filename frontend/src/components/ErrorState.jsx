import React from 'react';
import { AlertTriangle, RefreshCw, Terminal } from 'lucide-react';

export default function ErrorState({ error, onRetry, apiUrl = 'http://127.0.0.1:8000' }) {
  return (
    <div className="my-10 p-8 sm:p-10 bg-white rounded-2xl border border-rose-200 shadow-sm text-center flex flex-col items-center justify-center">
      <div className="w-14 h-14 rounded-2xl bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 mb-4">
        <AlertTriangle className="w-7 h-7" />
      </div>

      <h3 className="text-xl font-bold text-slate-900">
        Unable to connect to ShopGraph API
      </h3>
      <p className="text-sm text-slate-600 max-w-lg mt-2">
        Make sure the FastAPI backend is running on:
      </p>
      
      <div className="mt-3 px-3 py-1.5 bg-slate-100 rounded-lg text-xs font-mono text-slate-800 border border-slate-200 inline-flex items-center gap-2">
        <Terminal className="w-3.5 h-3.5 text-slate-500" />
        <span>{apiUrl}</span>
      </div>

      {error && (
        <div className="mt-3 text-xs text-rose-600 max-w-md bg-rose-50/70 p-2.5 rounded-lg border border-rose-100 text-left overflow-auto font-mono">
          {typeof error === 'string' ? error : error.message || 'API request failed'}
        </div>
      )}

      <div className="mt-6 flex flex-wrap gap-3 justify-center">
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm shadow-blue-500/20 transition-all active:scale-[0.98]"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Try Again</span>
          </button>
        )}
      </div>

      <div className="mt-6 pt-5 border-t border-slate-100 text-xs text-slate-400">
        Tip: Run <code className="text-slate-600 font-mono bg-slate-100 px-1.5 py-0.5 rounded">uvicorn app.main:app --reload</code> in the ShopGraph directory.
      </div>
    </div>
  );
}
