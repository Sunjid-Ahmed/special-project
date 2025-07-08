import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import eslint from 'vite-plugin-eslint'

export default defineConfig({
  plugins: [
    react(),
    eslint({
      failOnError: false,
      failOnWarning: false,
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    open: true,
  },
})