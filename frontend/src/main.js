import { createApp } from 'vue'
// 移除 Element 全局接入，避免与现有交互冲突；后续按需再开启
import './style.css'
import { initFontScaling } from './fontScale.js'

// Initialize global font scaling (Ctrl/Cmd + Wheel, +/-/0)
try { initFontScaling() } catch {}

const params = new URLSearchParams(window.location.search)
const view = params.get('view')

if (view === 'console') {
  import('./components/console/ConsoleManager.vue').then(mod => {
    const ConsoleManager = mod.default
    const app = createApp(ConsoleManager)
    app.mount('#app')
  })
} else {
  import('./App.vue').then(mod => {
    const App = mod.default
    const app = createApp(App)
    app.mount('#app')
  })
}
