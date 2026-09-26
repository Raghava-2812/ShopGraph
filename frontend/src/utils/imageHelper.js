/**
 * ShopGraph - Image Helper & Reliable Fallback Engine
 * frontend/src/utils/imageHelper.js
 *
 * Ensures 100% reliable image rendering. Broken images are automatically intercepted
 * and replaced with stylish, themed category SVG placeholders.
 */

// Generate an inline SVG Data URL for any category to guarantee zero broken images
export function createCategorySvg(category = 'Product', label = '') {
  const colors = {
    Laptops: { bg1: '#3b82f6', bg2: '#1d4ed8', icon: '💻' },
    'Gaming Laptops': { bg1: '#8b5cf6', bg2: '#6d28d9', icon: '⚡' },
    Monitors: { bg1: '#06b6d4', bg2: '#0e7490', icon: '🖥️' },
    Keyboards: { bg1: '#10b981', bg2: '#047857', icon: '⌨️' },
    Mice: { bg1: '#f59e0b', bg2: '#d97706', icon: '🖱️' },
    Headphones: { bg1: '#ec4899', bg2: '#be185d', icon: '🎧' },
    Earbuds: { bg1: '#f43f5e', bg2: '#e11d48', icon: '🎵' },
    Smartphones: { bg1: '#6366f1', bg2: '#4338ca', icon: '📱' },
    Tablets: { bg1: '#14b8a6', bg2: '#0f766e', icon: '📲' },
    'Smart Watches': { bg1: '#84cc16', bg2: '#65a30d', icon: '⌚' },
    Webcams: { bg1: '#0ea5e9', bg2: '#0284c7', icon: '📷' },
    Speakers: { bg1: '#eab308', bg2: '#ca8a04', icon: '🔊' },
    'USB Hubs': { bg1: '#64748b', bg2: '#475569', icon: '🔌' },
    Storage: { bg1: '#3b82f6', bg2: '#1e40af', icon: '💾' },
    'Power Banks': { bg1: '#10b981', bg2: '#065f46', icon: '🔋' },
    Backpacks: { bg1: '#78716c', bg2: '#57534e', icon: '🎒' },
    'Laptop Stands': { bg1: '#94a3b8', bg2: '#64748b', icon: '📐' },
    'Desk Lamps': { bg1: '#f97316', bg2: '#ea580c', icon: '💡' },
    'Office Chairs': { bg1: '#475569', bg2: '#334155', icon: '🪑' },
  };

  const theme = colors[category] || { bg1: '#3b82f6', bg2: '#1d4ed8', icon: '📦' };
  const displayLabel = label || category || 'ShopGraph Product';
  const cleanLabel = displayLabel.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').slice(0, 26);

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
    <defs>
      <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:${theme.bg1};stop-opacity:1" />
        <stop offset="100%" style="stop-color:${theme.bg2};stop-opacity:1" />
      </linearGradient>
    </defs>
    <rect width="600" height="400" fill="url(#grad)" rx="16"/>
    <circle cx="300" cy="170" r="75" fill="rgba(255,255,255,0.15)"/>
    <text x="300" y="195" font-size="64" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif">${theme.icon}</text>
    <text x="300" y="290" font-size="22" font-weight="700" fill="#ffffff" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif">${cleanLabel}</text>
    <text x="300" y="325" font-size="14" font-weight="500" fill="rgba(255,255,255,0.85)" text-anchor="middle" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif">${category}</text>
  </svg>`;

  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

/**
 * Handle image error and replace with styled SVG placeholder
 */
export function handleImageError(e, category = 'Product', name = '') {
  const target = e.target;
  if (!target.dataset.hasFailed) {
    target.dataset.hasFailed = 'true';
    target.src = createCategorySvg(category, name);
  }
}

/**
 * Get safe product image URL or default SVG
 */
export function getProductImageUrl(product) {
  if (product && product.image_url && product.image_url.startsWith('http')) {
    return product.image_url;
  }
  return createCategorySvg(product?.category, product?.name);
}
