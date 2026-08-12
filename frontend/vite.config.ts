import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/quant/',
  plugins: [react()],
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined
          if (id.includes('echarts') || id.includes('zrender')) return 'vendor-echarts'
          if (id.includes('react') || id.includes('scheduler')) return 'vendor-react'
          if (id.includes('lucide')) return 'vendor-icons'
          return 'vendor-misc'
        },
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/quant/api': {
        target: 'http://127.0.0.1:8000',
        rewrite: (path) => path.replace(/^\/quant\/api/, '/api'),
      },
    },
  },
})
