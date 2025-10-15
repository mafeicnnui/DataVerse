<template>
  <div class="tq-table-fixed" v-if="ctx?.tq?.result && ctx.tq.result.type === 'table'">
  <!-- 顶部仅用于显示表头，不作为横向滚动条容器（固定在结果区顶部） -->
    <div class="tq-scroll-x head-only" ref="tqScrollXRefLocal">
        <div class="tq-head-inner" :style="{ width: (ctx.tq.bodyTableWidth||0) + 'px' }">
          <table class="table tq-table" ref="tqHeadTableRefLocal" :style="{ width: (ctx.tq.bodyTableWidth||0) + 'px' }">
            <colgroup>
              <col v-for="(w, i) in ctx.tq.tableColWidths" :key="'h'+i" :style="w ? { width: w + 'px' } : {}">
            </colgroup>
            <thead>
              <tr>
                <th
                  v-for="(col, i) in ctx.tq.result.columns"
                  :key="'hcell'+i"
                  :class="{ 'freeze-head': i < ctx.tq.freezeCount }"
                  :style="i < ctx.tq.freezeCount ? { left: (ctx.tq.freezeLefts[i] || 0) + 'px' } : {}"
                >
                  <div class="th-inner">
                    <span class="th-title">{{ col }}</span>
                    <span class="th-actions">
                      <button class="th-btn lock" :aria-pressed="i < (ctx.tq.freezeCount||0)" :title="i < (ctx.tq.freezeCount||0) ? '解锁该列' : '锁定到此列'" @click.stop="ctx.headerLockClick(i)">
                        <svg v-if="i < (ctx.tq.freezeCount||0)" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a5 5 0 0 0-5 5v3H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5Zm0 2a3 3 0 0 1 3 3v3H9V7a3 3 0 0 1 3-3Z"/></svg>
                        <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M17 8V7a5 5 0 0 0-9.9-1h2.06A3 3 0 0 1 15 7v1h1a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h11Z"/></svg>
                      </button>
                      <button class="th-btn sort" :title="ctx.tq.sortKey===col ? (ctx.tq.sortDir==='asc' ? '升序' : '降序') : '排序'" @click.stop="ctx.toggleSort(col)">
                        <svg v-if="ctx.tq.sortKey===col && ctx.tq.sortDir==='asc'" viewBox="0 0 24 24" fill="currentColor"><path d="M7 14l5-5 5 5H7z"/></svg>
                        <svg v-else-if="ctx.tq.sortKey===col && ctx.tq.sortDir==='desc'" viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5H7z"/></svg>
                        <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M8 9h8l-4-4-4 4zm0 6h8l-4 4-4-4z"/></svg>
                      </button>
                    </span>
                  </div>
                  <span class="col-resizer" @mousedown.prevent="(e) => ctx.startColResize(i, e)"></span>
                </th>
              </tr>
            </thead>
          </table>
        </div>
      </div>
  <!-- 数据体：唯一滚动容器（横/纵）；直接使用自身横向滚动条，移除父级额外 x-scroll 的依赖 -->
    <div class="tq-body" ref="tqBodyRefLocal" @scroll="ctx.onBodyScroll" :style="{ overflowX: 'auto', overflowY: 'auto' }">
      <div class="tq-body-inner">
        <table class="table tq-table" ref="tqBodyTableRefLocal" :style="{ width: (ctx.tq.bodyTableWidth||0) + 'px' }">
          <colgroup>
            <col v-for="(w, i) in ctx.tq.tableColWidths" :key="'b'+i" :style="w ? { width: w + 'px' } : {}">
          </colgroup>
          <tbody :key="'tbody-'+ctx.tq.page+'-'+ctx.tq.pageSize">
            <tr v-for="(row, rIdx) in ctx.getDisplayedRows()" :key="'p'+ctx.tq.page+'-r'+rIdx+'-'+(row?.id ?? '')">
              <td
                v-for="(col, cIdx) in ctx.tq.result.columns"
                :key="'c'+cIdx"
                :class="[{ 'freeze-cell': cIdx < ctx.tq.freezeCount }]"
                :style="cIdx < ctx.tq.freezeCount ? { left: (ctx.tq.freezeLefts[cIdx] || 0) + 'px' } : {}"
              >{{ (row && row[col] !== undefined) ? row[col] : row?.[cIdx] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { inject, ref, onMounted, onBeforeUnmount, nextTick, onUpdated } from 'vue'

// 从上层注入上下文（tq + 方法 + refs 或回调）
const ctx = inject<any>('tqCtx')

// 本地 refs：如父需要访问，可在 mount 时回传或让父侧不再直接依赖这些具体 DOM 引用
const tqHeadTableRefLocal = ref<HTMLElement | null>(null)
const tqBodyTableRefLocal = ref<HTMLElement | null>(null)
const tqScrollXRefLocal = ref<HTMLElement | null>(null)
const tqBodyRefLocal = ref<HTMLElement | null>(null)

// 若父仍有需要，可在挂载后同步给父（保持兼容，减少改动）
onMounted(() => {
  if (!ctx) return
  if (ctx.tqHeadTableRef) ctx.tqHeadTableRef.value = tqHeadTableRefLocal.value
  if (ctx.tqBodyTableRef) ctx.tqBodyTableRef.value = tqBodyTableRefLocal.value
  if (ctx.tqScrollXRef) ctx.tqScrollXRef.value = tqScrollXRefLocal.value
  if (ctx.tqBodyRef) ctx.tqBodyRef.value = tqBodyRefLocal.value
  nextTick(() => {
    try {
      ctx.computeColWidths && ctx.computeColWidths()
      ctx.adjustHeaderGutter && ctx.adjustHeaderGutter()
    } catch {}
    // 强制一次横向同步：避免父组件重渲染后 .tq-body 被重置为 0
    try {
      const xs = ctx.tqScrollXRef?.value as HTMLElement | null
      const body = ctx.tqBodyRef?.value as HTMLElement | null
      if (xs && body && body.scrollLeft !== xs.scrollLeft) body.scrollLeft = xs.scrollLeft
    } catch {}
    try { ctx.syncBodyScroll && ctx.syncBodyScroll() } catch {}
  })
})

onUpdated(() => {
  // 子组件更新后再做一次横向同步，覆盖任何由 DOM 更新导致的 scrollLeft 重置
  try {
    const xs = (ctx && ctx.tqScrollXRef) ? ctx.tqScrollXRef.value as HTMLElement | null : null
    const body = (ctx && ctx.tqBodyRef) ? ctx.tqBodyRef.value as HTMLElement | null : null
    if (xs && body && body.scrollLeft !== xs.scrollLeft) body.scrollLeft = xs.scrollLeft
  } catch {}
  try { ctx && ctx.syncBodyScroll && ctx.syncBodyScroll() } catch {}
})

onBeforeUnmount(() => {
  if (!ctx) return
  if (ctx.tqBodyRef && ctx.tqBodyRef.value === tqBodyRefLocal.value) ctx.tqBodyRef.value = null
})
</script>

<style>
/* 结果表格局部样式（下沉自 App.vue，保证在子组件内生效） */
.tq-table-fixed { display: flex; flex-direction: column; width: 100%; flex: 1 1 0%; min-height: 0; position: relative; z-index: 1; }
.tq-scroll-x { position: sticky; top: 0; z-index: 2; background: #fff; border-bottom: 1px solid #e5e7eb; max-width: 100%; overflow-x: hidden; overflow-y: hidden; min-height: 16px; }
.tq-scroll-x.head-only { overflow: hidden; }
.tq-head-inner { display: inline-block; min-height: 36px; height: 36px; background: #fff; }
.tq-head-inner table { height: 36px; }

.tq-body { display:flex; flex-direction:column; width: 100%; max-width: 100%; flex: 1 1 0%; min-height: 0; max-height: 100%; overflow-x: auto; overflow-y: auto; -webkit-overflow-scrolling: touch; padding-bottom: var(--statusbar-h); box-sizing: border-box; }

.tq-table { border-collapse: separate; border-spacing: 0; width: max-content; table-layout: fixed; font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif; font-size: 14px; color: #111827; }
.tq-table thead { position: sticky; top: 0; z-index: 2; background: #f5f7ff; }
.tq-table th, .tq-table td { box-sizing: border-box; padding: 8px; border: 1px solid #eee; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 400; font-size: 14px; }
.tq-table thead th { background: #f5f7ff; position: relative; }

.tq-table tbody .freeze-cell { position: sticky; background: #fff; z-index: 4; top: auto; }
.tq-table thead th.freeze-head { position: sticky; left: 0; background: #f5f7ff; z-index: 12; }
.tq-table .freeze-cell::after { content: ''; position: absolute; top: 0; right: -1px; width: 1px; height: 100%; background: #e5e7eb; }

.tq-table .th-inner { display: flex; align-items: center; gap: 6px; padding-right: 0; }
.tq-table .th-title { flex: 1 1 auto; min-width: max-content; overflow: visible; text-overflow: clip; }
.tq-table .th-inner { white-space: nowrap; }
.tq-table .th-actions { position: static; transform: none; right: auto; top: auto; display: inline-flex; gap: 6px; flex: 0 0 auto; margin-right: 6px; z-index: 2; }
.tq-table .th-btn { width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; border: none; background: transparent; color: #64748b; cursor: pointer; padding: 0; }
.tq-table .th-btn:hover { color: #0b57d0; }
.tq-table .th-btn svg { width: 16px; height: 16px; }
.tq-table .col-resizer { position: absolute; top: 0; right: 0; width: 4px; height: 100%; cursor: col-resize; user-select: none; z-index: 4; }
.tq-table .col-resizer:hover { background: rgba(59,130,246,0.15); }

/* 滚动条外观（与父级保持一致） */
.tq-body { scrollbar-width: thin; scrollbar-color: #94a3b8 transparent; }
/* 仅显示纵向滚动条，隐藏横向滚动条（内部依然可编程滚动） */
.tq-body::-webkit-scrollbar { width: 10px; height: 10px; }
.tq-body::-webkit-scrollbar:horizontal { height: 12px; display: initial; }
.tq-body::-webkit-scrollbar:vertical { width: 10px; }
.tq-body::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 6px; }
.tq-body::-webkit-scrollbar-thumb:hover { background: #64748b; }
.tq-body::-webkit-scrollbar-thumb:active { background: #64748b; }
.tq-body::-webkit-scrollbar-track { background: transparent; }
/* 头部不显示滚动条 */
.tq-scroll-x { scrollbar-width: none; }
.tq-scroll-x::-webkit-scrollbar { height: 0; }
</style>
