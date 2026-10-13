/**
 * ShopGraph - Vite Frontend Bundler Configuration
 * File: frontend/vite.config.js
 *
 * Configures React plugin and dev server options (port 5173, host binding).
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Listen on all network interfaces
  },
});
