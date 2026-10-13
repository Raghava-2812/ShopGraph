/**
 * ShopGraph - Authentication State Context
 * File: frontend/src/context/AuthContext.jsx
 *
 * Provides application-wide authentication state and identity actions (login,
 * register, logout). Automatically initializes user session from localStorage
 * token on page reload via `/auth/me`.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api.js';

// Global context instance for authentication
const AuthContext = createContext(null);

/**
 * Authentication Provider Component
 *
 * Manages active user record, loading state, and token persistence in localStorage.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - Child component tree
 */
export function AuthProvider({ children }) {
  // Current user object: { id, name, email } or null
  const [user, setUser] = useState(null);
  // Indicates if initial session verification is in progress
  const [loading, setLoading] = useState(true);

  // Re-hydrate user profile from stored JWT token on mount
  useEffect(() => {
    const token = localStorage.getItem('shopgraph_token');
    if (token) {
      authAPI.me()
        .then(setUser)
        .catch(() => {
          // Token expired or invalid: purge from storage
          localStorage.removeItem('shopgraph_token');
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  /**
   * Log in user with credentials, save token, and update auth state.
   * @param {string} email
   * @param {string} password
   * @returns {Promise<Object>} API response with user details and token
   */
  const login = async (email, password) => {
    const data = await authAPI.login(email, password);
    localStorage.setItem('shopgraph_token', data.access_token);
    setUser({ id: data.user_id, name: data.name, email: data.email });
    return data;
  };

  /**
   * Register new user account, save token, and immediately log them in.
   * @param {string} name
   * @param {string} email
   * @param {string} password
   * @returns {Promise<Object>} API response with new user details and token
   */
  const register = async (name, email, password) => {
    const data = await authAPI.register(name, email, password);
    localStorage.setItem('shopgraph_token', data.access_token);
    setUser({ id: data.user_id, name: data.name, email: data.email });
    return data;
  };

  /**
   * Log out active user by clearing the JWT token and resetting user state.
   */
  const logout = () => {
    localStorage.removeItem('shopgraph_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Custom hook to consume the authentication context.
 *
 * @returns {{
 *   user: { id: number, name: string, email: string } | null,
 *   loading: boolean,
 *   login: (email: string, pass: string) => Promise<any>,
 *   register: (name: string, email: string, pass: string) => Promise<any>,
 *   logout: () => void
 * }}
 */
export const useAuth = () => useContext(AuthContext);
