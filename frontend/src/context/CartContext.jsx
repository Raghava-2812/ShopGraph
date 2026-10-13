/**
 * ShopGraph - Shopping Cart State Context
 * File: frontend/src/context/CartContext.jsx
 *
 * Manages the shopping cart state across the application, synchronizing line items,
 * quantities, and subtotal amounts with the FastAPI backend.
 *
 * Side Effects:
 *   - Automatically emits ADD_TO_CART and REMOVE_FROM_CART events to the telemetry
 *     pipeline, feeding the Neo4j personalized recommendation engine.
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import { cartAPI, eventsAPI } from '../services/api.js';
import { useAuth } from './AuthContext.jsx';

// Global context instance for cart data
const CartContext = createContext(null);

/**
 * Shopping Cart Provider Component
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child component tree
 */
export function CartProvider({ children }) {
  const { user } = useAuth();
  // Cart state structure: items array, total currency amount, total item count
  const [cart, setCart] = useState({ items: [], total: 0, item_count: 0 });
  const [loading, setLoading] = useState(false);

  /**
   * Fetch active cart from backend. Clears state if user is unauthenticated.
   */
  const fetchCart = useCallback(async () => {
    if (!user) {
      setCart({ items: [], total: 0, item_count: 0 });
      return;
    }
    setLoading(true);
    try {
      const data = await cartAPI.get();
      setCart(data);
    } catch (e) {
      console.error('Cart fetch error:', e);
    } finally {
      setLoading(false);
    }
  }, [user]);

  /**
   * Add a product to the cart and fire telemetry event.
   * @param {string} product_name - Name of product to add
   * @param {number} price - Unit price
   * @param {number} [quantity=1] - Quantity to add
   */
  const addToCart = useCallback(async (product_name, price, quantity = 1) => {
    if (!user) return;
    await cartAPI.addItem(product_name, quantity, price);
    // Fire recommendation event to boost product and related items
    await eventsAPI.record('ADD_TO_CART', product_name);
    await fetchCart();
  }, [user, fetchCart]);

  /**
   * Remove a line item by ID and emit removal telemetry event.
   * @param {number} item_id - Primary key of cart line item
   * @param {string} product_name - Product name for telemetry
   */
  const removeFromCart = useCallback(async (item_id, product_name) => {
    await cartAPI.removeItem(item_id);
    await eventsAPI.record('REMOVE_FROM_CART', product_name);
    await fetchCart();
  }, [fetchCart]);

  /**
   * Update quantity of an existing cart item. If quantity < 1, removes the item.
   * @param {number} item_id - Primary key of cart line item
   * @param {number} quantity - Target quantity
   */
  const updateQuantity = useCallback(async (item_id, quantity) => {
    if (quantity < 1) {
      await cartAPI.removeItem(item_id);
    } else {
      await cartAPI.updateItem(item_id, quantity);
    }
    await fetchCart();
  }, [fetchCart]);

  /**
   * Completely empty all items from active cart.
   */
  const clearCart = useCallback(async () => {
    await cartAPI.clear();
    setCart({ items: [], total: 0, item_count: 0 });
  }, []);

  return (
    <CartContext.Provider value={{ cart, loading, fetchCart, addToCart, removeFromCart, updateQuantity, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

/**
 * Custom hook to consume the shopping cart context.
 *
 * @returns {{
 *   cart: { items: Array<any>, total: number, item_count: number },
 *   loading: boolean,
 *   fetchCart: () => Promise<void>,
 *   addToCart: (name: string, price: number, qty?: number) => Promise<void>,
 *   removeFromCart: (id: number, name: string) => Promise<void>,
 *   updateQuantity: (id: number, qty: number) => Promise<void>,
 *   clearCart: () => Promise<void>
 * }}
 */
export const useCart = () => useContext(CartContext);
