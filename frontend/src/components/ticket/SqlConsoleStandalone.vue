<template>
  <div class="dv-sql-console-standalone">
    <!-- 直接复用 Shell，页面模式 -->
    <SqlConsoleShell mode="page" :init-conn-id="connId" />
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
</script>

<style scoped>
.dv-sql-console-standalone { display: block; height: 100vh; }
</style>
