<template>
  <div class="dv-sql-console-standalone">
    <!-- 直接复用 Shell，页面模式 -->
    <SqlConsoleShell mode="page" :init-conn-id="connId" :init-db="initDb" :init-sql="initSql" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import SqlConsoleShell from './SqlConsoleShell.vue'

const sp = new URLSearchParams(window.location.search)
const raw = sp.get('connId') || sp.get('connectionId') || sp.get('conn_id') || ''
const connId = computed(() => {
  const n = Number(raw)
  return Number.isFinite(n) && n > 0 ? n : raw
})
const initDb = computed(() => sp.get('database') || sp.get('db') || sp.get('schema') || '')
const initSql = computed(() => {
  const s = sp.get('sql') || ''
  try { return decodeURIComponent(s) } catch { return s }
})

// 独立页的“回主页面打开浮动控制台”已移至 SqlConsoleShell 工具栏图标，不再在此处提供按钮。
</script>

<style scoped>
.dv-sql-console-standalone { display: block; height: 100vh; }
</style>
