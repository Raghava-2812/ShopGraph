import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { wishlistAPI } from '../services/api.js';
import { useAuth } from './AuthContext.jsx';

const WishlistContext = createContext(null);

export function WishlistProvider({ children }) {
  const { user } = useAuth();
  const [wishlistItems, setWishlistItems] = useState([]);
  const [wishlistNames, setWishlistNames] = useState(new Set());
  const [loading, setLoading] = useState(false);

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

  useEffect(() => {
    fetchWishlist();
  }, [fetchWishlist]);

  const isWishlisted = useCallback((productName) => {
    return wishlistNames.has(productName);
  }, [wishlistNames]);

  const toggleWishlist = useCallback(async (product) => {
    if (!user) return false;
    const prodName = typeof product === 'string' ? product : product.name;
    const currentlyWishlisted = wishlistNames.has(prodName);

    // Optimistic state update
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
        // Rollback on error
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
        // Rollback on error
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

export const useWishlist = () => useContext(WishlistContext);
