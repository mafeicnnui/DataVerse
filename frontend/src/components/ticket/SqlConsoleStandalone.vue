<template>
  <div class="dv-sql-console-standalone">
    <div class="topbar">
      <button class="btn" title="在主页面打开浮动控制台" @click="openModalInOpener">在主页面打开浮动控制台</button>
      <span class="muted" v-if="!canNotify">无法找到主页面（或跨域），请手动切回主页面打开浮动控制台</span>
    </div>
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

const canNotify = !!(window.opener && (() => { try { return window.opener.location.origin === window.location.origin } catch { return false } })())

function openModalInOpener() {
  try {
    if (!window.opener) throw new Error('no opener')
    // 仅同源窗口允许 postMessage + focus
    const same = (() => { try { return window.opener.location.origin === window.location.origin } catch { return false } })()
    if (!same) throw new Error('different origin')
    window.opener.postMessage({ type: 'open-sql-modal', payload: { connId: connId.value, database: initDb.value, sql: initSql.value } }, window.location.origin)
    try { window.opener.focus() } catch {}
  } catch {
    alert('未检测到主页面或跨域，无法自动打开。请手动切回主页面。')
  }
}
</script>

<style scoped>
.dv-sql-console-standalone { display: block; height: 100vh; }
.topbar { padding: 8px 12px; border-bottom: 1px solid #e5e7eb; background: #fff; display:flex; align-items:center; gap:10px; }
.btn { height: 28px; padding: 0 10px; border: 1px solid #c7d2fe; border-radius: 6px; background: #e6f0ff; color: #0b57d0; cursor: pointer; }
.muted { color:#9ca3af; font-size: 12px; }
</style>
