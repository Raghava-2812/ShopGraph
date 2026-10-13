/**
 * ShopGraph - Frontend API Client & Service Layer
 * File: frontend/src/services/api.js
 *
 * Centralized HTTP client configured with Axios.
 * Manages base URLs, timeout settings, JSON headers, and automatic JWT injection.
 *
 * Exposes scoped domain modules:
 *   - authAPI: User registration, login, and profile lookup
 *   - productsAPI: Product catalog, full-text search, brands, categories
 *   - eventsAPI: Behavioral telemetry tracking (VIEW, CART, PURCHASE, SEARCH)
 *   - recommendationsAPI: Personalized and graph-based product recommendations
 *   - wishlistAPI: User wishlist CRUD
 *   - cartAPI: Persistent shopping cart management
 *   - ordersAPI: Checkout, order placement, and history
 */

import axios from 'axios';

// Base URL resolves from Vite environment variables or defaults to local FastAPI
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Pre-configured Axios instance with 15s timeout
const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

/**
 * Request Interceptor: Attach JWT Bearer Token
 * Inspects localStorage on every outgoing request. If a token exists,
 * injects it into the Authorization header to authenticate requests.
 */
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('shopgraph_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Authentication API ────────────────────────────────────────────────────────

/**
 * Authentication and identity service methods.
 */
export const authAPI = {
  /**
   * Register a new user account.
   * @param {string} name - User's full name
   * @param {string} email - Unique email address
   * @param {string} password - Raw password (will be hashed server-side)
   */
  register: (name, email, password) =>
    client.post('/auth/register', { name, email, password }).then(r => r.data),

  /**
   * Authenticate an existing user and receive a JWT token.
   * @param {string} email - Registered email address
   * @param {string} password - User password
   */
  login: (email, password) =>
    client.post('/auth/login', { email, password }).then(r => r.data),

  /**
   * Fetch the currently authenticated user's profile based on the JWT token.
   */
  me: () => client.get('/auth/me').then(r => r.data),
};

// ── Products Catalog API ──────────────────────────────────────────────────────

/**
 * Product catalog exploration, filtering, and search endpoints.
 */
export const productsAPI = {
  /**
   * Retrieve products with optional filtering by category, brand, or sorting.
   * Accepts either a category string or an object with query parameters.
   * @param {string|Object} params - Query filters ({ category, brand, sort })
   */
  list: (params = {}) => {
    const queryParams = typeof params === 'string' ? { category: params } : params;
    return client.get('/products', { params: queryParams }).then(r => r.data);
  },

  /**
   * Search catalog products by name, category, brand, or feature query.
   * @param {string} q - Search keyword
   */
  search: (q) =>
    client.get('/products/search', { params: { q } }).then(r => r.data),

  /**
   * Fetch all distinct categories available in the knowledge graph.
   */
  categories: () => client.get('/products/categories').then(r => r.data),

  /**
   * Fetch all distinct brands present in the knowledge graph.
   */
  brands: () => client.get('/products/brands').then(r => r.data),

  /**
   * Fetch all products associated with a specific category.
   * @param {string} cat - Category name
   */
  byCategory: (cat) => client.get(`/products/category/${encodeURIComponent(cat)}/products`).then(r => r.data),

  /**
   * Fetch complete knowledge graph metadata for a single product.
   * @param {string} name - Exact product name
   */
  getOne: (name) => client.get(`/products/${encodeURIComponent(name)}`).then(r => r.data),
};

// ── Behavioral Events Telemetry API ───────────────────────────────────────────

/**
 * User behavior telemetry tracking.
 * Used by recommendation engines to refine personalization weights.
 */
export const eventsAPI = {
  /**
   * Record a behavioral telemetry event. Silently skips for unauthenticated guests.
   * @param {'VIEW'|'ADD_TO_CART'|'REMOVE_FROM_CART'|'PURCHASE'|'SEARCH'|'WISHLIST'} event_type
   * @param {string|null} product_name - Target product name
   * @param {string|null} search_query - Query string if event is SEARCH
   * @param {string|null} category_name - Category context if applicable
   */
  record: (event_type, product_name = null, search_query = null, category_name = null) => {
    const token = localStorage.getItem('shopgraph_token');
    if (!token) return Promise.resolve(null); // Silently skip for guests
    return client
      .post('/events', { event_type, product_name, search_query, category_name })
      .then(r => r.data)
      .catch(() => null);
  },
};

// ── Recommendation Engine API ─────────────────────────────────────────────────

/**
 * Knowledge Graph and multi-signal recommendation endpoints.
 */
export const recommendationsAPI = {
  /**
   * Get graph-based recommendations related to a specific product.
   * @param {string} name - Product name
   * @param {number} top_k - Maximum recommendations to return
   */
  forProduct: (name, top_k = 6) =>
    client.get(`/recommendations/product/${encodeURIComponent(name)}`, { params: { top_k } }).then(r => r.data),

  /**
   * Get cross-selling recommendations tailored to the user's active shopping cart.
   */
  forCart: () => client.get('/recommendations/cart').then(r => r.data),

  /**
   * Get personalized recommendations blending graph relations and historical behavior.
   * @param {number} top_k - Maximum recommendations to return
   */
  personalized: (top_k = 8) =>
    client.get('/recommendations', { params: { top_k } }).then(r => r.data),

  /**
   * Fetch the list of products recently viewed by the logged-in user.
   * @param {number} limit - Maximum products to retrieve
   */
  recentlyViewed: (limit = 8) =>
    client.get('/recommendations/recently-viewed', { params: { limit } }).then(r => r.data),

  /**
   * Get top recommended products within a specific category.
   * @param {string} categoryName - Category name
   * @param {number} top_k - Maximum recommendations to return
   */
  forCategory: (categoryName, top_k = 6) =>
    client.get(`/recommendations/category/${encodeURIComponent(categoryName)}`, { params: { top_k } }).then(r => r.data),
};

// ── Wishlist API ──────────────────────────────────────────────────────────────

/**
 * User wishlist endpoints.
 */
export const wishlistAPI = {
  /**
   * Fetch all wishlisted items enriched with knowledge graph details.
   */
  get: () => client.get('/wishlist').then(r => r.data),

  /**
   * Add a product to the user's wishlist.
   * @param {string} product_name - Target product name
   */
  add: (product_name) => client.post(`/wishlist/${encodeURIComponent(product_name)}`).then(r => r.data),

  /**
   * Remove a product from the user's wishlist.
   * @param {string} product_name - Target product name
   */
  remove: (product_name) => client.delete(`/wishlist/${encodeURIComponent(product_name)}`).then(r => r.data),

  /**
   * Check whether a specific product is in the user's wishlist.
   * @param {string} product_name - Target product name
   */
  check: (product_name) => client.get(`/wishlist/check/${encodeURIComponent(product_name)}`).then(r => r.data),
};

// ── Shopping Cart API ─────────────────────────────────────────────────────────

/**
 * User shopping cart endpoints.
 */
export const cartAPI = {
  /**
   * Retrieve active shopping cart with all items, subtotal, and item count.
   */
  get: () => client.get('/cart').then(r => r.data),

  /**
   * Add a product line item to the cart.
   * @param {string} product_name - Product name
   * @param {number} quantity - Quantity to add
   * @param {number} price - Unit price
   */
  addItem: (product_name, quantity, price) =>
    client.post('/cart/items', { product_name, quantity, price }).then(r => r.data),

  /**
   * Update the quantity of an existing cart line item.
   * @param {number} id - Cart item ID
   * @param {number} quantity - New quantity
   */
  updateItem: (id, quantity) =>
    client.patch(`/cart/items/${id}`, { quantity }).then(r => r.data),

  /**
   * Remove a single line item from the shopping cart.
   * @param {number} id - Cart item ID
   */
  removeItem: (id) => client.delete(`/cart/items/${id}`).then(r => r.data),

  /**
   * Clear all items from the current user's shopping cart.
   */
  clear: () => client.delete('/cart').then(r => r.data),
};

// ── Orders & Checkout API ─────────────────────────────────────────────────────

/**
 * Order placement and purchase history endpoints.
 */
export const ordersAPI = {
  /**
   * Convert active shopping cart into an order with shipping address.
   * @param {Object} shipping - Shipping information object
   */
  create: (shipping) => client.post('/orders', { shipping }).then(r => r.data),

  /**
   * List all historical orders for the authenticated user.
   */
  list: () => client.get('/orders').then(r => r.data),

  /**
   * Fetch full details for a single order by ID.
   * @param {number} id - Order ID
   */
  getOne: (id) => client.get(`/orders/${id}`).then(r => r.data),
};

// ── Backwards-Compatible Export Aliases (used by legacy Home demo) ──────────────

/**
 * Legacy wrapper: Fetch list of products.
 */
export const getProducts = (params) => productsAPI.list(params);

/**
 * Legacy wrapper: Fetch recommendations for a specific product.
 */
export const getRecommendations = (name, top_k = 5) => recommendationsAPI.forProduct(name, top_k);

/**
 * Legacy wrapper: Fetch detailed graph metadata for a product.
 */
export const getProductDetails = (name) => productsAPI.getOne(name);

/**
 * Legacy wrapper: Check API health endpoint.
 */
export const getHealth = () => client.get('/health').then(r => r.data);

export { API_BASE_URL };
export default client;
