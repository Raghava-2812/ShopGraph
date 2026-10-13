/**
 * ShopGraph - Frontend Application Entry Point
 * File: frontend/src/main.jsx
 *
 * Mounts the root React component tree into the HTML document root (#root).
 * Wraps the app in React.StrictMode to highlight potential side-effect issues
 * and deprecated APIs during development.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

// Mount the top-level React component tree
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
