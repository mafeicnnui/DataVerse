import { createApp } from 'vue'
import './style.css'

const params = new URLSearchParams(window.location.search)
const view = params.get('view')

if (view === 'console') {
  import('./components/console/ConsoleManager.vue').then(mod => {
    const ConsoleManager = mod.default
    createApp(ConsoleManager).mount('#app')
  })
} else {
  import('./App.vue').then(mod => {
    const App = mod.default
    createApp(App).mount('#app')
  })
}
