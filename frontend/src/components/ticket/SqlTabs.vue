<template>
  <div class="tq-tabbar" role="tablist" aria-label="SQL 标签">
    <div
      v-for="(tab, idx) in ctx.tq.qTabs"
      :key="tab.id"
      class="tq-tab"
      :class="{ active: tab.id === ctx.tq.activeQueryTabId }"
      role="tab"
      :aria-selected="tab.id === ctx.tq.activeQueryTabId"
      :title="tab.title"
      @click="ctx.activateQueryTab(tab.id)"
      tabindex="0"
    >
      <span class="ico" aria-hidden="true">▤</span>
      <span class="tit">{{ tab.title }}</span>
      <!-- 单一圆点：活跃 或 未保存 -> 显示，避免重复两个圆点 -->
      <span v-if="tab.ui?.dirty || tab.id === ctx.tq.activeQueryTabId" class="dot" :title="tab.ui?.dirty ? '未保存' : '当前标签'">•</span>
      <button class="close" title="关闭" @click.stop="ctx.closeQueryTab(tab.id)">×</button>
    </div>
    <button class="tq-tab add" title="新建 (Ctrl+T)" @click="ctx.newQueryTab()">＋</button>
  </div>
</template>

<script setup lang="ts">
import { inject } from 'vue'
const ctx = inject<any>('tqCtx')
</script>

<style>
/* Tab 样式（从父组件拷贝，保证子组件内可用） */
.tq-tabbar { display: flex; align-items: center; gap: 6px; padding: 6px 6px 4px; border-bottom: 1px solid #e5e7eb; margin-bottom: 6px; }
.tq-tabbar .tq-tab { position: relative; display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; padding-right: 26px; background: #f3f4f6; border: 1px solid #e5e7eb; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; color: #0b57d0; font-size: 13px; font-weight: 400; overflow: visible; }
.tq-tabbar .tq-tab.active { background: #fff; border-color: #c7d2fe; z-index: 2; }
.tq-tabbar .tq-tab .ico { font-size: 12px; opacity: .8; }
.tq-tabbar .tq-tab .tit { max-width: 160px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tq-tabbar .tq-tab .dot { color: #9ca3af; margin-left: 2px; }
.tq-tabbar .tq-tab.active .dot { color: #ef4444; }
.tq-tabbar .tq-tab > .close { position: absolute; top: 2px; right: 3px; width: 14px; height: 14px; font-size: 11px; line-height: 12px; display: inline-flex; align-items: center; justify-content: center; border-radius: 3px; opacity: .8; cursor: pointer; padding: 0 !important; border: none !important; background: transparent !important; min-width: 0 !important; box-sizing: content-box; }
.tq-tabbar .tq-tab > .close:hover { background: #e5e7eb; opacity: 1; }
/* 新建（+）按钮：仅显示 +，无边框/背景，更紧凑 */
.tq-tabbar .tq-tab.add { border: none !important; background: transparent !important; padding: 0 6px !important; color: #0b57d0; font-size: 16px; line-height: 1; height: 24px; display: inline-flex; align-items: center; justify-content: center; }
.tq-tabbar .tq-tab.add:hover { background: transparent !important; color: #1d4ed8; }
</style>
