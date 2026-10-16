import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  return {
    plugins: [react()],
    test: { environment: 'jsdom', setupFiles: './src/test-setup.ts', globals: true },
    server: {
      proxy: {
        '/health': env.VITE_API_TARGET ?? 'http://localhost:8000',
        '/api': env.VITE_API_TARGET ?? 'http://localhost:8000',
        '/uploads': env.VITE_API_TARGET ?? 'http://localhost:8000',
      },
    },
  };
});
