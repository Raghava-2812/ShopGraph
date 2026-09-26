import React, { createContext, useContext, useState, useCallback } from 'react';
import { cartAPI, eventsAPI } from '../services/api.js';
import { useAuth } from './AuthContext.jsx';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState({ items: [], total: 0, item_count: 0 });
  const [loading, setLoading] = useState(false);

  const fetchCart = useCallback(async () => {
    if (!user) { setCart({ items: [], total: 0, item_count: 0 }); return; }
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

  const addToCart = useCallback(async (product_name, price, quantity = 1) => {
    if (!user) return;
    await cartAPI.addItem(product_name, quantity, price);
    await eventsAPI.record('ADD_TO_CART', product_name);
    await fetchCart();
  }, [user, fetchCart]);

  const removeFromCart = useCallback(async (item_id, product_name) => {
    await cartAPI.removeItem(item_id);
    await eventsAPI.record('REMOVE_FROM_CART', product_name);
    await fetchCart();
  }, [fetchCart]);

  const updateQuantity = useCallback(async (item_id, quantity) => {
    if (quantity < 1) {
      await cartAPI.removeItem(item_id);
    } else {
      await cartAPI.updateItem(item_id, quantity);
    }
    await fetchCart();
  }, [fetchCart]);

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

export const useCart = () => useContext(CartContext);
