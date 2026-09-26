import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request if available
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('shopgraph_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth API
export const authAPI = {
  register: (name, email, password) =>
    client.post('/auth/register', { name, email, password }).then(r => r.data),
  login: (email, password) =>
    client.post('/auth/login', { email, password }).then(r => r.data),
  me: () => client.get('/auth/me').then(r => r.data),
};

// Products API
export const productsAPI = {
  list: (params = {}) => {
    // Support category string or full params object { category, brand, sort }
    const queryParams = typeof params === 'string' ? { category: params } : params;
    return client.get('/products', { params: queryParams }).then(r => r.data);
  },
  search: (q) =>
    client.get('/products/search', { params: { q } }).then(r => r.data),
  categories: () => client.get('/products/categories').then(r => r.data),
  brands: () => client.get('/products/brands').then(r => r.data),
  byCategory: (cat) => client.get(`/products/category/${encodeURIComponent(cat)}/products`).then(r => r.data),
  getOne: (name) => client.get(`/products/${encodeURIComponent(name)}`).then(r => r.data),
};

// Events API
export const eventsAPI = {
  record: (event_type, product_name = null, search_query = null, category_name = null) => {
    const token = localStorage.getItem('shopgraph_token');
    if (!token) return Promise.resolve(null); // silently skip for guests
    return client
      .post('/events', { event_type, product_name, search_query, category_name })
      .then(r => r.data)
      .catch(() => null);
  },
};

// Recommendations API
export const recommendationsAPI = {
  forProduct: (name, top_k = 6) =>
    client.get(`/recommendations/product/${encodeURIComponent(name)}`, { params: { top_k } }).then(r => r.data),
  forCart: () => client.get('/recommendations/cart').then(r => r.data),
  personalized: (top_k = 8) =>
    client.get('/recommendations', { params: { top_k } }).then(r => r.data),
  recentlyViewed: (limit = 8) =>
    client.get('/recommendations/recently-viewed', { params: { limit } }).then(r => r.data),
  forCategory: (categoryName, top_k = 6) =>
    client.get(`/recommendations/category/${encodeURIComponent(categoryName)}`, { params: { top_k } }).then(r => r.data),
};

// Wishlist API
export const wishlistAPI = {
  get: () => client.get('/wishlist').then(r => r.data),
  add: (product_name) => client.post(`/wishlist/${encodeURIComponent(product_name)}`).then(r => r.data),
  remove: (product_name) => client.delete(`/wishlist/${encodeURIComponent(product_name)}`).then(r => r.data),
  check: (product_name) => client.get(`/wishlist/check/${encodeURIComponent(product_name)}`).then(r => r.data),
};

// Cart API
export const cartAPI = {
  get: () => client.get('/cart').then(r => r.data),
  addItem: (product_name, quantity, price) =>
    client.post('/cart/items', { product_name, quantity, price }).then(r => r.data),
  updateItem: (id, quantity) =>
    client.patch(`/cart/items/${id}`, { quantity }).then(r => r.data),
  removeItem: (id) => client.delete(`/cart/items/${id}`).then(r => r.data),
  clear: () => client.delete('/cart').then(r => r.data),
};

// Orders API
export const ordersAPI = {
  create: (shipping) => client.post('/orders', { shipping }).then(r => r.data),
  list: () => client.get('/orders').then(r => r.data),
  getOne: (id) => client.get(`/orders/${id}`).then(r => r.data),
};

export { API_BASE_URL };
export default client;
