import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Check backend health
 */
export async function getHealth() {
  const response = await client.get('/');
  return response.data;
}

/**
 * Retrieve all products from the Knowledge Graph.
 * Returns an array of product objects or strings.
 */
export async function getProducts() {
  const response = await client.get('/products');
  return response.data;
}

/**
 * Retrieve full product details and Neo4j graph relationships.
 * (Category, Brand, Features, Use Cases, Compatible items, Accessories, etc.)
 */
export async function getProductDetails(productName) {
  const response = await client.get(`/products/${encodeURIComponent(productName)}`);
  return response.data;
}

/**
 * Retrieve explainable recommendations from the Knowledge Graph.
 */
export async function getRecommendations(productName, topK = 5) {
  const response = await client.get(
    `/recommend/${encodeURIComponent(productName)}`,
    {
      params: { top_k: topK },
    }
  );
  return response.data;
}

export default {
  getHealth,
  getProducts,
  getProductDetails,
  getRecommendations,
  API_BASE_URL,
};
