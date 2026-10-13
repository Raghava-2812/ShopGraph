/**
 * ShopGraph - Wishlist State Context
 * File: frontend/src/context/WishlistContext.jsx
 *
 * Manages user saved/favorite products across the application.
 *
 * Key Design Pattern:
 *   - Employs Optimistic UI Updates: when the user toggles a product, local state
 *     updates immediately to provide an instantaneous UI response. If the backend
 *     network call fails, the state automatically rolls back by re-fetching from the server.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { wishlistAPI } from '../services/api.js';
import { useAuth } from './AuthContext.jsx';

// Global context instance for wishlist data
const WishlistContext = createContext(null);

/**
 * Wishlist Provider Component
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child component tree
 */
export function WishlistProvider({ children }) {
  const { user } = useAuth();
  // Array of detailed wishlist product objects
  const [wishlistItems, setWishlistItems] = useState([]);
  // Set of product names for fast O(1) membership checks
  const [wishlistNames, setWishlistNames] = useState(new Set());
  const [loading, setLoading] = useState(false);

  /**
   * Fetch user's wishlist from the backend. Clears state if unauthenticated.
   */
  const fetchWishlist = useCallback(async () => {
    if (!user) {
      setWishlistItems([]);
      setWishlistNames(new Set());
      return;
    }
    setLoading(true);
    try {
      const data = await wishlistAPI.get();
      const items = data.items || [];
      setWishlistItems(items);
      setWishlistNames(new Set(items.map(i => i.name)));
    } catch (e) {
      console.error('Wishlist fetch error:', e);
    } finally {
      setLoading(false);
    }
  }, [user]);

  // Synchronize wishlist whenever the active user changes
  useEffect(() => {
    fetchWishlist();
  }, [fetchWishlist]);

  /**
   * Check if a product is in the user's wishlist (O(1) Set lookup).
   * @param {string} productName - Product name to check
   * @returns {boolean} True if wishlisted
   */
  const isWishlisted = useCallback((productName) => {
    return wishlistNames.has(productName);
  }, [wishlistNames]);

  /**
   * Toggle a product in/out of the wishlist with optimistic updates.
   * @param {string|Object} product - Product name string or product object
   * @returns {Promise<boolean>} Resolves to true if added, false if removed
   */
  const toggleWishlist = useCallback(async (product) => {
    if (!user) return false;
    const prodName = typeof product === 'string' ? product : product.name;
    const currentlyWishlisted = wishlistNames.has(prodName);

    // Optimistic state update: update UI before waiting for network response
    if (currentlyWishlisted) {
      setWishlistNames(prev => {
        const next = new Set(prev);
        next.delete(prodName);
        return next;
      });
      setWishlistItems(prev => prev.filter(i => i.name !== prodName));
      try {
        await wishlistAPI.remove(prodName);
      } catch (err) {
        // Rollback on network/server error
        fetchWishlist();
      }
      return false;
    } else {
      setWishlistNames(prev => new Set(prev).add(prodName));
      if (typeof product === 'object') {
        setWishlistItems(prev => [product, ...prev]);
      }
      try {
        await wishlistAPI.add(prodName);
      } catch (err) {
        // Rollback on network/server error
        fetchWishlist();
      }
      return true;
    }
  }, [user, wishlistNames, fetchWishlist]);

  return (
    <WishlistContext.Provider
      value={{
        wishlistItems,
        wishlistNames,
        wishlistCount: wishlistNames.size,
        isWishlisted,
        toggleWishlist,
        fetchWishlist,
        loading,
      }}
    >
      {children}
    </WishlistContext.Provider>
  );
}

/**
 * Custom hook to consume the wishlist context.
 *
 * @returns {{
 *   wishlistItems: Array<any>,
 *   wishlistNames: Set<string>,
 *   wishlistCount: number,
 *   isWishlisted: (name: string) => boolean,
 *   toggleWishlist: (product: any) => Promise<boolean>,
 *   fetchWishlist: () => Promise<void>,
 *   loading: boolean
 * }}
 */
export const useWishlist = () => useContext(WishlistContext);
