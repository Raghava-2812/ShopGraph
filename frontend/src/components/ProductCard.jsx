import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Tag, ChevronRight } from 'lucide-react';

export default function ProductCard({ product }) {
  const navigate = useNavigate();

  const { name, price, category, brand, description } = product;

  const handleClick = () => {
    navigate(`/products/${encodeURIComponent(name)}`);
  };

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer group"
    >
      {/* Product Image Placeholder */}
      <div className="h-40 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-t-xl flex items-center justify-center">
        <div className="text-4xl font-bold text-blue-200">
          {name.charAt(0)}
        </div>
      </div>

      <div className="p-4">
        {category && (
          <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
            {category}
          </span>
        )}
        <h3 className="mt-2 font-semibold text-slate-800 text-sm leading-snug group-hover:text-blue-600 transition-colors">
          {name}
        </h3>
        {brand && (
          <p className="text-xs text-slate-400 mt-0.5">{brand}</p>
        )}
        <div className="mt-3 flex items-center justify-between">
          <span className="text-base font-bold text-slate-800">
            {price ? `₹${price.toLocaleString('en-IN')}` : 'Price unavailable'}
          </span>
          <span className="text-blue-600 group-hover:translate-x-1 transition-transform">
            <ChevronRight className="w-4 h-4" />
          </span>
        </div>
      </div>
    </div>
  );
}
