/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
  plugins: [react()],
  server: {host: '127.0.0.1', port: 5175, proxy: {
    '/api/v5': 'http://127.0.0.1:8005',
    '/docs': 'http://127.0.0.1:8005',
    '/openapi.json': 'http://127.0.0.1:8005',
  }},
  test: {environment: 'jsdom', globals: true},
});
