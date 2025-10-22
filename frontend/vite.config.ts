import { defineConfig } from 'vite'

export default defineConfig(({ mode }) => ({
  base: process.env.VITE_BASE_PATH || (mode === 'production' ? '/good-neighbor/' : '/'),
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: '../dist',
  },
  test: {
    globals: true,
    environment: 'jsdom',
  },
}))
