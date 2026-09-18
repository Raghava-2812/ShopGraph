import React from 'react';
import { Network, Cpu, Database, ExternalLink, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Navbar({ apiHealthy = true, onOpenGraphInfo }) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight text-slate-900">ShopGraph</span>
              <span className="hidden sm:inline-block text-[11px] font-semibold uppercase tracking-wider bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full border border-blue-200">
                Neo4j KG
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">Knowledge Graph Recommendations</p>
          </div>
        </div>

        {/* Right navigation items */}
        <div className="flex items-center gap-3 sm:gap-6">
          {/* API Status */}
          <div className="flex items-center gap-1.5 text-xs font-medium text-slate-600 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-full">
            {apiHealthy ? (
              <>
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="hidden sm:inline">API</span> Online
              </>
            ) : (
              <>
                <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                <span className="hidden sm:inline">API</span> Offline
              </>
            )}
          </div>

          <a
            href="#knowledge-graph-section"
            className="flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
          >
            <Database className="w-4 h-4 text-blue-500" />
            <span>Knowledge Graph</span>
          </a>

          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
            title="FastAPI Swagger Documentation"
          >
            <Cpu className="w-4 h-4 text-slate-500" />
            <span>API Docs</span>
            <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
          </a>
        </div>
      </div>
    </header>
  );
}
