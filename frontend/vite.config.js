import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'node:fs';

const isDocker = fs.existsSync('/.dockerenv');
const backendTarget =
  process.env.VITE_BACKEND_TARGET ||
  (isDocker ? 'http://backend:8000' : 'http://localhost:8000');

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
});
