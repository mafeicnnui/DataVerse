import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 允许通过环境变量覆盖后端地址（便于在局域网访问时不使用 127.0.0.1）
// 使用方法（示例）：
//   VITE_API_TARGET=http://10.16.45.135:8001 npm run dev
const apiTarget = process.env.VITE_API_TARGET || 'http://10.16.45.135:8001'


export default defineConfig({
  plugins: [vue()],
  server: {
    // 对外网/局域网可访问
    host: true, // 等同于 '0.0.0.0'
    port: 5173,
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
        ws: true,
      },
    },
  },
})
