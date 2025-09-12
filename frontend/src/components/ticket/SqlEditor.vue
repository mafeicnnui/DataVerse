<template>
  <div class="tq-editor" :style="{ '--tq-editor-h': (ctx.tq.editorHeight || 120) + 'px', flexBasis: (ctx.tq.editorHeight || 120) + 'px', height: (ctx.tq.editorHeight || 120) + 'px' }" ref="tqEditorRefLocal">
    <div ref="tqCodeRefLocal" class="tq-sql" role="textbox" aria-label="SQL 编辑器" title="在此编写 SQL... 支持 Ctrl+Enter 执行" @click="ctx.onSqlHostClick" tabindex="0"></div>
  </div>
  <div
    class="tq-resizer"
    title="拖动以调整编辑器与结果区域高度"
    @mousedown.prevent="ctx.startResize"
  ></div>
</template>

<script setup lang="ts">
import { inject, ref, onMounted, watch, nextTick } from 'vue'
const ctx = inject<any>('tqCtx')
const tqEditorRefLocal = ref<HTMLElement | null>(null)
const tqCodeRefLocal = ref<HTMLElement | null>(null)

onMounted(() => {
  if (!ctx) return
  if (ctx.tqEditorRef) ctx.tqEditorRef.value = tqEditorRefLocal.value
  if (ctx.tqCodeRef) ctx.tqCodeRef.value = tqCodeRefLocal.value
  // 父级已有 ensureSqlEditor 与激活时机，这里不强制调用，保持兼容
})

// 高度变化后触发一次重排，帮助编辑器根据新高度刷新布局
watch(() => ctx?.tq?.editorHeight, async () => {
  await nextTick()
  try {
    // 通知浏览器做一次重排，兼容性最好
    window.dispatchEvent(new Event('resize'))
  } catch {}
  try {
    const el = tqEditorRefLocal.value as HTMLElement | null
    if (el && ctx?.tq?.editorHeight) {
      el.style.height = `${ctx.tq.editorHeight}px`
      el.style.flexBasis = `${ctx.tq.editorHeight}px`
    }
  } catch {}
})
</script>

<style>
/* 下沉自 App.vue 的编辑器容器样式，确保在子组件内生效 */
.tq-editor { display:flex; flex-direction: column; flex: 0 0 var(--tq-editor-h); min-height: 100px; position: relative; z-index: 20; overflow: visible; height: var(--tq-editor-h) !important; }
/* 提升选择器优先级，覆盖父组件 .ticket-query .tq-editor 的 flex:0 0 auto */
.ticket-query .tq-editor { flex: 0 0 var(--tq-editor-h) !important; height: var(--tq-editor-h) !important; }

/* 让 SQL 容器与 CodeMirror 占满高度（避免父组件 scoped 样式失效） */
.tq-sql { width: 100%; height: 100%; min-height: 0; flex: 1 1 auto; resize: none; padding: 0; border: none; border-radius: 0; position: relative; overflow: hidden; }
.tq-sql :deep(.cm-editor) {
  width: 100%;
  height: 100% !important;
  min-height: 0;
  box-sizing: border-box;
  padding: 10px;
  border:1px solid #e5e7eb;
  border-radius: 8px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 13px;
  line-height: 1.6;
}
.tq-sql :deep(.cm-editor .cm-scroller) { height: 100% !important; overflow: auto !important; overflow-y: auto !important; }
.tq-sql :deep(.cm-editor .cm-content) { min-height: 100% !important; }
.tq-sql :deep(.cm-editor .cm-content) { white-space: pre-wrap; }
.tq-editor :deep(.cm-editor) { border-bottom: none; box-shadow: none; outline: none; }

/* 分隔线可视化：在 12px 高度中间画一条淡灰线，便于拖拽定位 */
/* 控制台统一使用 App.vue 的 .tq-vsplit 作为唯一分割条，这里隐藏组件内的 .tq-resizer */
.tq-resizer { display: none !important; }
.tq-resizer::before, .tq-resizer::after { display: none !important; content: none !important; }
</style>
