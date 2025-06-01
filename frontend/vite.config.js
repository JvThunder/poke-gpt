import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/create_chat': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      '/query': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      '/chat_history': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
