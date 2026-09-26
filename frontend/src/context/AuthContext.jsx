import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('shopgraph_token');
    if (token) {
      authAPI.me()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('shopgraph_token');
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const data = await authAPI.login(email, password);
    localStorage.setItem('shopgraph_token', data.access_token);
    setUser({ id: data.user_id, name: data.name, email: data.email });
    return data;
  };

  const register = async (name, email, password) => {
    const data = await authAPI.register(name, email, password);
    localStorage.setItem('shopgraph_token', data.access_token);
    setUser({ id: data.user_id, name: data.name, email: data.email });
    return data;
  };

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

export const useAuth = () => useContext(AuthContext);
