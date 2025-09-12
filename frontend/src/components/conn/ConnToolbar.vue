<template>
  <div class="toolbar card" style="display:flex; gap:14px; align-items:center; flex-wrap: wrap; width:100%; box-sizing:border-box;">
    <div class="field icon-left" title="类型">
      <svg class="leading" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <rect x="4" y="4" width="7" height="7" rx="1.5"/>
        <rect x="13" y="4" width="7" height="7" rx="1.5"/>
        <rect x="4" y="13" width="7" height="7" rx="1.5"/>
        <rect x="13" y="13" width="7" height="7" rx="1.5"/>
      </svg>
      <select v-model="localFilter.type" class="with-icon" @change="emitUpdate" aria-label="类型">
        <option value="">全部类型</option>
        <option v-for="opt in dictType" :key="opt.dmm" :value="opt.dmm">{{ opt.dmmc }}</option>
      </select>
    </div>
    <div class="field icon-left" title="环境">
      <svg class="leading" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="9"/>
        <path d="M3 12h18"/>
        <path d="M12 3v18"/>
      </svg>
      <select v-model="localFilter.env" class="with-icon" @change="emitUpdate" aria-label="环境">
        <option value="">全部环境</option>
        <option v-for="opt in dictEnv" :key="opt.dmm" :value="opt.dmm">{{ opt.dmmc }}</option>
      </select>
    </div>
    <div class="field icon-left" title="状态">
      <svg class="leading" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="9"/>
        <path d="M8 12.5l2.5 2.5L16 9"/>
      </svg>
      <select v-model="localFilter.status" class="with-icon" @change="emitUpdate" aria-label="状态">
        <option value="">全部状态</option>
        <option v-for="opt in dictStatus" :key="opt.dmm" :value="opt.dmm">{{ opt.dmmc }}</option>
      </select>
    </div>
    <div class="actions" role="group" aria-label="查询与新增" style="display:flex; align-items:center; gap:6px;">
      <button class="icon-btn test" @click="$emit('query')" title="查询" aria-label="查询">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
          <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 5 1.5-1.5-5-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        </svg>
      </button>
      <button class="icon-btn info" @click="$emit('create')" title="新增" aria-label="新增">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
          <path d="M19 11h-6V5h-2v6H5v2h6v6h2v-6h6z"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  filter: { type: Object, required: true },
  dictType: { type: Array, default: () => [] },
  dictEnv: { type: Array, default: () => [] },
  dictStatus: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:filter', 'query', 'create'])

const localFilter = reactive({ type: '', env: '', status: '' })

watch(() => props.filter, (v) => {
  localFilter.type = v.type || ''
  localFilter.env = v.env || ''
  localFilter.status = v.status || ''
}, { immediate: true, deep: true })

function emitUpdate() {
  emit('update:filter', { ...localFilter })
}
</script>

<style scoped>
.card { background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 12px; box-sizing: border-box; }
.toolbar { border: none !important; outline: none; box-shadow: none; }
/* 当 toolbar 同时具有 card 类时，强制显示白色卡片背景并占满一行 */
.toolbar.card { background: #fff; width: 100%; box-sizing: border-box; }
.toolbar select { font-size: 14px; color: #0b57d0; font-weight: 400; height: 30px; border: 1px solid #e5e7eb; border-radius: 6px; background: #fff; padding: 0 8px; }
/* 内嵌图标：与 HostManager 保持一致 */
.field { position: relative; display: inline-flex; align-items: center; }
.field .leading { position: absolute; left: 8px; color: #64748b; }
.toolbar select.with-icon { padding-left: 30px; }
.icon-btn { display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:6px; border:1px solid #c9c9c9; background:#fff; color:#333; cursor:pointer; }
/* 与表格操作列保持一致的按钮配色 */
.icon-btn.info { border-color:#3b82f6; color:#0b57d0; background:#e8f0fe; }
.icon-btn.info:hover { background:#dbe8ff; }
.icon-btn.test { border-color:#22c55e; color:#15803d; background:#eefdf3; }
.icon-btn.test:hover { background:#dcfce7; }

/* 不使用连体按钮组，改为与表格操作列相同的独立按钮效果，由父容器gap控制间距 */
</style>
