import React from 'react';
import { Network, ArrowDown, Cpu, Sparkles, Layers, Box, Tag, Compass } from 'lucide-react';

export default function KnowledgeGraph({
  selectedProduct,
  recommendations = [],
  productDetails,
}) {
  const topRec = recommendations.length > 0 ? recommendations[0] : null;
  const secondRec = recommendations.length > 1 ? recommendations[1] : null;

  // Derive nodes from productDetails or fallback
  const features = productDetails?.features || ['USB-C', 'Bluetooth', 'WiFi'];
  const useCases = productDetails?.use_cases || ['Office Work', 'Work From Home'];

  const targetNode1 = topRec ? topRec.product : 'Dell USB-C Hub';
  const targetNode2 = secondRec ? secondRec.product : 'Dell Laptop Stand';
  const featureNode = features[0] || 'USB-C';
  const useCaseNode = useCases[0] || 'Office Work';

  return (
    <section id="knowledge-graph-section" className="mt-12 sm:mt-16 space-y-10">
      {/* 1. Visual Relationship Diagram */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1 rounded bg-blue-100 text-blue-700">
                <Network className="w-4 h-4" />
              </span>
              <span className="text-xs font-bold uppercase tracking-wider text-blue-700">
                Knowledge Graph Subgraph
              </span>
            </div>
            <h3 className="text-xl font-bold text-slate-900 mt-1">
              Active Graph Traversal: <span className="text-blue-600">{selectedProduct || 'Selected Product'}</span>
            </h3>
          </div>
          <p className="text-xs text-slate-500 font-medium">
            SVG Node-Link Schema Representation
          </p>
        </div>

        {/* Responsive Interactive SVG Graph Canvas */}
        <div className="relative bg-slate-900 rounded-2xl p-4 sm:p-8 overflow-hidden shadow-inner border border-slate-800">
          {/* Subtle grid background */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:24px_24px] opacity-40"></div>

          <div className="relative z-10 w-full overflow-x-auto">
            <svg
              viewBox="0 0 800 420"
              className="w-full max-w-3xl mx-auto h-auto min-w-[620px]"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                {/* Arrowhead marker */}
                <marker
                  id="arrow-blue"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#3b82f6" />
                </marker>
                <marker
                  id="arrow-emerald"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#10b981" />
                </marker>
                <marker
                  id="arrow-purple"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#a855f7" />
                </marker>
                <marker
                  id="arrow-amber"
                  viewBox="0 0 10 10"
                  refX="8"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#f59e0b" />
                </marker>

                {/* Gradients */}
                <linearGradient id="coreGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#2563eb" />
                  <stop offset="100%" stopColor="#1d4ed8" />
                </linearGradient>
              </defs>

              {/* ── EDGES ──────────────────────────────────────────────────────── */}
              {/* Core to Top Feature */}
              <line
                x1="220"
                y1="210"
                x2="390"
                y2="90"
                stroke="#3b82f6"
                strokeWidth="2.5"
                strokeDasharray="4 2"
                markerEnd="url(#arrow-blue)"
              />
              {/* Rec1 to Top Feature */}
              <line
                x1="570"
                y1="210"
                x2="410"
                y2="90"
                stroke="#3b82f6"
                strokeWidth="2.5"
                strokeDasharray="4 2"
                markerEnd="url(#arrow-blue)"
              />

              {/* Core to Rec 1 (Direct Relationship) */}
              <line
                x1="240"
                y1="210"
                x2="550"
                y2="210"
                stroke="#10b981"
                strokeWidth="3"
                markerEnd="url(#arrow-emerald)"
              />

              {/* Core to Use Case */}
              <line
                x1="220"
                y1="210"
                x2="390"
                y2="330"
                stroke="#a855f7"
                strokeWidth="2"
                markerEnd="url(#arrow-purple)"
              />
              {/* Rec1 to Use Case */}
              <line
                x1="570"
                y1="210"
                x2="410"
                y2="330"
                stroke="#a855f7"
                strokeWidth="2"
                markerEnd="url(#arrow-purple)"
              />

              {/* Core to Rec 2 (Accessory / Similar) */}
              <line
                x1="200"
                y1="235"
                x2="200"
                y2="335"
                stroke="#f59e0b"
                strokeWidth="2.5"
                markerEnd="url(#arrow-amber)"
              />

              {/* ── EDGE LABELS ────────────────────────────────────────────────── */}
              {/* HAS_FEATURE Left */}
              <rect x="250" y="125" width="105" height="22" rx="6" fill="#1e293b" stroke="#3b82f6" strokeWidth="1" />
              <text x="302" y="140" fill="#93c5fd" fontSize="10" fontFamily="sans-serif" fontWeight="bold" textAnchor="middle">
                HAS_FEATURE
              </text>

              {/* HAS_FEATURE Right */}
              <rect x="440" y="125" width="105" height="22" rx="6" fill="#1e293b" stroke="#3b82f6" strokeWidth="1" />
              <text x="492" y="140" fill="#93c5fd" fontSize="10" fontFamily="sans-serif" fontWeight="bold" textAnchor="middle">
                HAS_FEATURE
              </text>

              {/* COMPATIBLE_WITH Center */}
              <rect x="330" y="198" width="135" height="24" rx="6" fill="#064e3b" stroke="#10b981" strokeWidth="1.5" />
              <text x="397" y="214" fill="#a7f3d0" fontSize="11" fontFamily="sans-serif" fontWeight="bold" textAnchor="middle">
                COMPATIBLE_WITH
              </text>

              {/* USED_FOR */}
              <rect x="260" y="275" width="85" height="20" rx="6" fill="#1e293b" stroke="#a855f7" strokeWidth="1" />
              <text x="302" y="289" fill="#d8b4fe" fontSize="10" fontFamily="sans-serif" fontWeight="bold" textAnchor="middle">
                USED_FOR
              </text>

              {/* ACCESSORY Down */}
              <rect x="150" y="280" width="100" height="20" rx="6" fill="#1e293b" stroke="#f59e0b" strokeWidth="1" />
              <text x="200" y="294" fill="#fde68a" fontSize="10" fontFamily="sans-serif" fontWeight="bold" textAnchor="middle">
                ACCESSORY
              </text>

              {/* ── NODES ──────────────────────────────────────────────────────── */}
              {/* 1. Core Purchased Product (Left) */}
              <g transform="translate(200, 210)">
                <circle r="46" fill="url(#coreGlow)" stroke="#60a5fa" strokeWidth="3" filter="drop-shadow(0 4px 6px rgba(0,0,0,0.5))" />
                <text y="-8" fill="#ffffff" fontSize="11" fontWeight="bold" textAnchor="middle">
                  PURCHASED
                </text>
                <text y="10" fill="#ffffff" fontSize="12" fontWeight="800" textAnchor="middle">
                  {selectedProduct ? (selectedProduct.length > 15 ? selectedProduct.substring(0, 14) + '…' : selectedProduct) : 'Purchased Product'}
                </text>
              </g>

              {/* 2. Top Feature Node (Top Center) */}
              <g transform="translate(400, 75)">
                <rect x="-70" y="-22" width="140" height="44" rx="12" fill="#1e3a8a" stroke="#60a5fa" strokeWidth="2" />
                <text y="-4" fill="#93c5fd" fontSize="9" fontWeight="bold" textAnchor="middle">FEATURE</text>
                <text y="14" fill="#ffffff" fontSize="12" fontWeight="bold" textAnchor="middle">{featureNode}</text>
              </g>

              {/* 3. Primary Recommended Node (Right) */}
              <g transform="translate(590, 210)">
                <circle r="46" fill="#065f46" stroke="#34d399" strokeWidth="3" />
                <text y="-8" fill="#a7f3d0" fontSize="11" fontWeight="bold" textAnchor="middle">
                  RECOMMENDED
                </text>
                <text y="10" fill="#ffffff" fontSize="12" fontWeight="800" textAnchor="middle">
                  {targetNode1.length > 15 ? targetNode1.substring(0, 14) + '…' : targetNode1}
                </text>
              </g>

              {/* 4. Use Case Node (Bottom Center) */}
              <g transform="translate(400, 345)">
                <rect x="-75" y="-22" width="150" height="44" rx="12" fill="#581c87" stroke="#c084fc" strokeWidth="2" />
                <text y="-4" fill="#e9d5ff" fontSize="9" fontWeight="bold" textAnchor="middle">USE CASE</text>
                <text y="14" fill="#ffffff" fontSize="12" fontWeight="bold" textAnchor="middle">{useCaseNode}</text>
              </g>

              {/* 5. Second Recommended Node / Accessory (Bottom Left) */}
              <g transform="translate(200, 360)">
                <rect x="-85" y="-20" width="170" height="40" rx="10" fill="#78350f" stroke="#fbbf24" strokeWidth="2" />
                <text y="-3" fill="#fde68a" fontSize="9" fontWeight="bold" textAnchor="middle">RECOMMENDED ACC</text>
                <text y="13" fill="#ffffff" fontSize="11" fontWeight="bold" textAnchor="middle">
                  {targetNode2.length > 18 ? targetNode2.substring(0, 17) + '…' : targetNode2}
                </text>
              </g>
            </svg>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-[11px] text-slate-400">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> Purchased Item</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Recommended Item</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-blue-900 border border-blue-400"></span> Feature Node</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded bg-purple-900 border border-purple-400"></span> Use Case Node</span>
            </div>
            <span className="text-slate-500">Rendered from live Neo4j subgraph relationships</span>
          </div>
        </div>
      </div>

      {/* 2. "How ShopGraph thinks" Section (Section 14) */}
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-8">
        <div className="max-w-2xl mx-auto text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold mb-2 border border-indigo-100">
            <Layers className="w-3.5 h-3.5" />
            <span>Algorithmic Reasoning</span>
          </div>
          <h3 className="text-2xl font-bold tracking-tight text-slate-900">
            How ShopGraph Thinks
          </h3>
          <p className="text-sm text-slate-600 mt-2 leading-relaxed">
            ShopGraph does not recommend products randomly.
            It explores relationships between products, features,
            categories and use cases stored in the Neo4j knowledge graph.
          </p>
        </div>

        {/* Reasoning Flow Pipeline */}
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 relative">
            {[
              { title: 'Purchased Product', desc: 'Seed node anchored in graph', icon: Box, color: 'border-blue-200 bg-blue-50/70 text-blue-700' },
              { title: 'Graph Relationships', desc: 'Direct edges (COMPATIBLE, ACCESSORY)', icon: Network, color: 'border-emerald-200 bg-emerald-50/70 text-emerald-700' },
              { title: 'Features', desc: 'Shared hardware specs & ports', icon: Cpu, color: 'border-cyan-200 bg-cyan-50/70 text-cyan-700' },
              { title: 'Use Cases', desc: 'Common application scenarios', icon: Compass, color: 'border-purple-200 bg-purple-50/70 text-purple-700' },
              { title: 'Compatible Products', desc: 'Candidate generator pool', icon: Tag, color: 'border-amber-200 bg-amber-50/70 text-amber-700' },
              { title: 'Recommendation Score', desc: 'Weighted transparent ranking', icon: Sparkles, color: 'border-indigo-200 bg-indigo-50/70 text-indigo-700' },
            ].map((step, idx) => {
              const IconComp = step.icon;
              return (
                <div
                  key={idx}
                  className={`p-4 rounded-xl border ${step.color} flex flex-col items-center text-center justify-between relative group hover:shadow-sm transition-all`}
                >
                  <div className="w-9 h-9 rounded-lg bg-white shadow-xs flex items-center justify-center mb-2">
                    <IconComp className="w-5 h-5 text-current" />
                  </div>
                  <div>
                    <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 block mb-0.5">
                      Step 0{idx + 1}
                    </span>
                    <h5 className="text-xs font-bold text-slate-900 leading-tight">
                      {step.title}
                    </h5>
                    <p className="text-[11px] text-slate-600 mt-1 leading-snug">
                      {step.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
