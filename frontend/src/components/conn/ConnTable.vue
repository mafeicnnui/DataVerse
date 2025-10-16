<template>
  <div class="cm-table-fixed">
    <!-- 独立表头：不参与纵向滚动，仅同步横向滚动 -->
    <div class="cm-scroll-x" ref="cmScrollXRef">
      <div class="cm-head-inner" :style="{ width: bodyTableWidth + 'px' }">
        <table class="table cm-table" :style="{ width: bodyTableWidth + 'px' }" ref="headTableRef">
          <colgroup>
            <col v-for="(w, i) in tableColWidths" :key="'h-col'+i" :style="{ width: w + 'px' }" />
            <col :style="{ width: opColWidth + 'px' }" />
          </colgroup>
          <thead>
            <tr>
              <th v-for="(col, i) in columns" :key="'h'+i" :class="{ 'freeze-head': i < freezeCount }" :style="i < freezeCount ? { left: (freezeLefts[i] || 0) + 'px' } : {}">
                <div class="th-inner">
                  <span class="th-title" :title="col">{{ col }}</span>
                  <span class="th-actions">
                    <button class="th-btn lock" :aria-pressed="i < freezeCount" :title="i < freezeCount ? '解锁该列' : '锁定到此列'" @click.stop="headerLockClick(i)">
                      <svg v-if="i < freezeCount" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a5 5 0 0 0-5 5v3H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5Zm0 2a3 3 0 0 1 3 3v3H9V7a3 3 0 0 1 3-3Z"/></svg>
                      <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M17 8V7a5 5 0 0 0-9.9-1h2.06A3 3 0 0 1 15 7v1h1a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h11Z"/></svg>
                    </button>
                    <button class="th-btn sort" :title="sortKey===keys[i] ? (sortDir==='asc' ? '升序' : sortDir==='desc' ? '降序' : '无序') : '排序'" @click.stop="toggleSort(i)">
                      <svg v-if="sortKey===keys[i] && sortDir==='asc'" viewBox="0 0 24 24" fill="currentColor"><path d="M7 14l5-5 5 5H7z"/></svg>
                      <svg v-else-if="sortKey===keys[i] && sortDir==='desc'" viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5H7z"/></svg>
                      <svg v-else viewBox="0 0 24 24" fill="currentColor"><path d="M8 9h8l-4-4-4 4zm0 6h8l-4 4-4-4z"/></svg>
                    </button>
                  </span>
                </div>
              </th>
              <th class="op-col">操作</th>
            </tr>
          </thead>
        </table>
      </div>
    </div>

    <!-- 数据体：唯一滚动容器（横/纵） -->
    <div class="cm-body" ref="cmBodyRef" @scroll="onBodyScroll">
      <div class="cm-body-inner">
        <table class="table cm-table" :style="{ width: bodyTableWidth + 'px' }" ref="bodyTableRef">
          <colgroup>
            <col v-for="(w, i) in tableColWidths" :key="'b-col'+i" :style="{ width: w + 'px' }" />
            <col :style="{ width: opColWidth + 'px' }" />
          </colgroup>
          <tbody>
            <tr v-for="item in sortedItems" :key="item.id">
              <td v-for="(k, cIdx) in keys" :key="'c'+cIdx" :class="[{ 'freeze-cell': cIdx < freezeCount }]" :style="cIdx < freezeCount ? { left: (freezeLefts[cIdx] || 0) + 'px' } : {}">
                {{ cellText(item, k) }}
              </td>
              <td class="op-col">
                <button class="icon-btn sm info" @click="$emit('edit', item)" title="编辑" aria-label="编辑">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zm3.92.83H5v-1.92L14.06 6.02l1.92 1.92L6.92 18.08zM20.71 5.63a.996.996 0 0 0 0-1.41L19.78 3.3a.996.996 0 1 0-1.41 1.41l.93.93c.39.39 1.02.39 1.41-.01z"/>
                  </svg>
                </button>
                <button class="icon-btn sm warn" @click="$emit('delete', item)" title="删除" aria-label="删除">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
                    <path d="M9 4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2h4v2H5V4h4zm2 0a0 0 0 0 0 0 0h2a0 0 0 0 0 0 0H11z"/>
                    <path d="M6 8h12l-1 12a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L6 8zM10 11v8h2v-8h-2zm4 0v8h2v-8h-2zM8 11v8h2v-8H8z"/>
                  </svg>
                </button>
                <button class="icon-btn sm success" @click="$emit('test', item)" title="测试" aria-label="测试">
                  <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true">
                    <path d="M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                  </svg>
                </button>
                <button class="icon-btn sm console" @click="$emit('console', item)" title="SQL 控制台" aria-label="SQL 控制台">
                  <!-- 简洁 SQL 图标：仅 'SQL' + 下方输入行与光标（无外框） -->
                  <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
                    <!-- SQL 文字（等宽字体更像代码） -->
                    <text x="12" y="10" text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace" font-size="7.6" font-weight="700" fill="currentColor">SQL</text>
                    <!-- 输入感：下方两条语句线 + 光标 -->
                    <path d="M6.5 13.8h7.2" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
                    <path d="M6.5 16.6h5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
                    <path d="M15.5 13.1v4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
                  </svg>
                </button>
                <!-- Next 版独立控制台（新窗口） -->
                <button class="icon-btn sm next" @click="openNextStandalone(item)" title="Next 控制台(新窗口)" aria-label="Next 控制台(新窗口)">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">
                    <!-- sparkles 图标，表示新一代 -->
                    <path d="M14 3l1.5 3.5L19 8l-3.5 1.5L14 13l-1.5-3.5L9 8l3.5-1.5L14 3Zm-6 6l1 2.5L12 13l-3 1.5L8 17l-1-2.5L4 13l3-1.5L8 9Zm10 5l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2Z"/>
                  </svg>
                </button>
                <!-- 独立控制台（新窗口）：紧挨在 SQL 控制台 右侧 -->
                <button class="icon-btn sm" @click="openStandalone(item)" title="独立控制台(新窗口)" aria-label="独立控制台(新窗口)">
                  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true">
                    <path d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3ZM5 5h7v2H7v10h10v-5h2v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z"/>
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 统一分页样式（与工单查询一致） -->
    <div class="tq-pagination">
      <button class="icon-btn" @click="$emit('prev')" :disabled="page<=1" title="上一页">‹</button>
      <span class="muted">第 {{ page }} / {{ totalPages }} 页</span>
      <input class="page-input" type="number" :min="1" :max="totalPages" :value="page" @keydown.enter.prevent="$emit('prev')" style="width:84px;margin:0 6px;padding:4px 6px;border:1px solid #c7d2fe;border-radius:6px;" title="输入页码后按回车跳转" />
      <button class="icon-btn" @click="$emit('next')" :disabled="page>=totalPages" title="下一页">›</button>
      <span class="muted" style="margin-left:8px;">每页</span>
      <select :value="pageSize" @change="onPageSizeChange">
        <option :value="20">20</option>
        <option :value="50">50</option>
        <option :value="100">100</option>
      </select>
      <span class="muted">条，共 {{ itemsTotal || 0 }} 条</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  dictType: { type: Array, default: () => [] },
  dictEnv: { type: Array, default: () => [] },
  dictStatus: { type: Array, default: () => [] },
  page: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
  totalPages: { type: Number, default: 1 },
  itemsTotal: { type: Number, default: 0 }
})

const emits = defineEmits(['edit','delete','test','console','prev','next','update:page-size'])

// 表头列（隐藏“创建时间”）
const columns = [
  '标识','描述','环境','类型','状态','更新时间'
]
// 对应数据键（与 columns 顺序一一对应）
const keys = ['id','description','db_env','db_type','status','update_time']

// 列宽（与头/体共享）——与 keys 长度一致（去掉“创建时间”后共6列）
const tableColWidths = ref([80,280,100,100,100,180])
// 追加“操作”列表头宽度（为新增 Next 按钮留出空间）
const opColWidth = 200
// 总宽=数据列之和 + 操作列宽
const bodyTableWidth = computed(() => (tableColWidths.value || []).reduce((s,n)=>s+(Number(n)||0),0) + opColWidth)
const freezeCount = ref(0)
const cmScrollXRef = ref(null)
const cmBodyRef = ref(null)
const bodyTableRef = ref(null)
const headTableRef = ref(null)
const headerGutter = ref(0)
let resizeObserver = null

// 冻结列 left 偏移
const freezeLefts = computed(() => {
  const arr = []
  let sum = 0
  const count = Number(freezeCount.value || 0)
  for (let i = 0; i < count; i++) {
    arr[i] = sum
    sum += Number((tableColWidths.value || [])[i] || 0)
  }
  return arr
})

function onBodyScroll() {
  try {
    if (!cmScrollXRef.value || !cmBodyRef.value) return
    cmScrollXRef.value.scrollLeft = cmBodyRef.value.scrollLeft
    adjustHeaderGutter()
  } catch {}
}

function getScrollbarWidth(el) {
  if (!el) return 0
  return (el.offsetWidth || 0) - (el.clientWidth || 0)
}

function adjustHeaderGutter() {
  try {
    if (!cmScrollXRef.value || !cmBodyRef.value) return
    const gutter = getScrollbarWidth(cmBodyRef.value)
    headerGutter.value = gutter || 0
    if (cmScrollXRef.value) cmScrollXRef.value.style.paddingRight = (gutter || 0) + 'px'
  } catch {}
}

function openStandalone(item) {
  try {
    const id = item?.id
    if (!id) return
    const url = `/db-console.html?connId=${encodeURIComponent(id)}`
    // 不使用 noopener，保证同源时 window.opener 可用于回到主页面打开浮动层
    window.open(url, '_blank')
  } catch {}
}

function openNextStandalone(item) {
  try {
    const id = item?.id
    if (!id) return
    // 指向 Next 版独立页（使用同源相对路径，避免硬编码主机与端口）
    const url = `/db-console-next.html?connId=${encodeURIComponent(id)}`
    window.open(url, '_blank')
  } catch {}
}

// 仅针对“表头标题可见性”的最小宽度适配：
// 计算每个表头的标题区与操作图标区所需宽度，如果当前列宽不足，则增大该列宽度。
async function fitHeaderWidthsToTitles() {
  await nextTick()
  try {
    const head = headTableRef.value
    if (!head) return
    const ths = Array.from(head.querySelectorAll('thead th'))
    if (!ths.length) return
    // 跳过最后一个“操作”表头
    const count = Math.min(tableColWidths.value.length, ths.length - 1)
    // 等一帧，确保字体与布局稳定
    await new Promise(r => requestAnimationFrame(r))
    const newWidths = [...tableColWidths.value]
    for (let i = 0; i < count; i++) {
      const th = ths[i]
      const titleEl = th.querySelector('.th-title')
      const actionsEl = th.querySelector('.th-actions')
      const cs = window.getComputedStyle(th)
      const pl = parseFloat(cs.paddingLeft) || 0
      const pr = parseFloat(cs.paddingRight) || 0
      const gap = 6
      const titleNeed = titleEl ? Math.ceil(titleEl.scrollWidth) : 0
      const actionsNeed = actionsEl ? Math.ceil(actionsEl.scrollWidth) : 0
      // 额外余量，避免边界截断
      const extra = 8
      const need = titleNeed + (actionsNeed ? gap + actionsNeed : 0) + pl + pr + extra
      const curr = Number(newWidths[i] || 0)
      if (need > curr) newWidths[i] = need
    }
    // 仅当有变化时再赋值，避免不必要的响应式抖动
    const changed = newWidths.some((w, i) => w !== tableColWidths.value[i])
    if (changed) tableColWidths.value = newWidths
  } catch {}
}

// 同步列宽（暂时关闭自动同步，回退到静态列宽以稳定 UI）
const enableAutoSync = false
async function syncColWidths() {
  if (!enableAutoSync) return
  await nextTick()
  try {
    const head = headTableRef.value
    const body = bodyTableRef.value
    if (!head) return
    const headRow = head.querySelector('thead tr')
    const bodyRow = body?.querySelector('tbody tr')
    if (!headRow) return
    const ths = Array.from(headRow.children || [])
    // 量测内容区宽度（content-box）
    const measureTh = () => ths.map((th) => {
      const rect = th.getBoundingClientRect()
      const cs = window.getComputedStyle(th)
      const pl = parseFloat(cs.paddingLeft) || 0
      const pr = parseFloat(cs.paddingRight) || 0
      const bl = parseFloat(cs.borderLeftWidth) || 0
      const br = parseFloat(cs.borderRightWidth) || 0
      return Math.max(0, Math.round((rect.width - pl - pr - bl - br) * 10) / 10)
    })
    const measureTd = () => {
      if (!bodyRow) return []
      const tds = Array.from(bodyRow.children || [])
      return tds.map(td => {
        const rect = td.getBoundingClientRect()
        const cs = window.getComputedStyle(td)
        const pl = parseFloat(cs.paddingLeft) || 0
        const pr = parseFloat(cs.paddingRight) || 0
        const bl = parseFloat(cs.borderLeftWidth) || 0
        const br = parseFloat(cs.borderRightWidth) || 0
        return Math.max(0, Math.round((rect.width - pl - pr - bl - br) * 10) / 10)
      })
    }

    let thW = measureTh()
    let tdW = measureTd()
    // 再次在下一帧测量，避免首次布局尚未稳定
    await new Promise(r => requestAnimationFrame(r))
    const thW2 = measureTh()
    const tdW2 = measureTd()
    // 取两次测量的最大值，减少抖动
    if (thW2.length === thW.length) thW = thW.map((w,i)=>Math.max(w, thW2[i]))
    if (tdW2.length === tdW.length && tdW.length) tdW = tdW.map((w,i)=>Math.max(w, tdW2[i] || 0))

    // 汇总为每列最大值（表头与数据体）
    const widths = thW.map((w,i)=>Math.max(w, tdW[i] || 0))
    // 最后一列是操作列，保持固定宽度规则，若存在则沿用测量值
    if (widths && widths.length) {
      tableColWidths.value = widths
    }
  } catch {}
}

// 锁列切换
function headerLockClick(i) {
  try {
    const next = i + 1
    if (Number(freezeCount.value) === next) {
      freezeCount.value = 0
    } else {
      freezeCount.value = next
    }
  } catch {}
}

// 排序
const sortKey = ref('')
const sortDir = ref('') // '', 'asc', 'desc'
function toggleSort(i) {
  const k = keys[i]
  if (!k) return
  if (sortKey.value !== k) {
    sortKey.value = k
    sortDir.value = 'asc'
  } else if (sortDir.value === 'asc') {
    sortDir.value = 'desc'
  } else if (sortDir.value === 'desc') {
    sortKey.value = ''
    sortDir.value = ''
  } else {
    sortDir.value = 'asc'
  }
}

const sortedItems = computed(() => {
  const arr = Array.isArray(props.items) ? [...props.items] : []
  if (!sortKey.value || !sortDir.value) return arr
  const k = sortKey.value
  const dir = sortDir.value
  arr.sort((a,b) => {
    const va = a?.[k]
    const vb = b?.[k]
    // 时间列尝试转 Date
    const parseMaybeDate = (v) => {
      if (v == null) return v
      if (typeof v === 'string' && /[:\-T]/.test(v)) {
        const d = new Date(v)
        const t = d.getTime()
        return Number.isNaN(t) ? v : t
      }
      return v
    }
    const A = parseMaybeDate(va)
    const B = parseMaybeDate(vb)
    if (A == null && B == null) return 0
    if (A == null) return dir==='asc' ? -1 : 1
    if (B == null) return dir==='asc' ? 1 : -1
    if (A === B) return 0
    return (A > B ? 1 : -1) * (dir==='asc' ? 1 : -1)
  })
  return arr
})

function cellText(item, k) {
  if (k === 'db_type') return labelOf(props.dictType, item?.[k])
  if (k === 'db_env') return labelOf(props.dictEnv, item?.[k])
  if (k === 'status') return labelOf(props.dictStatus, item?.[k])
  if (k === 'create_time' || k === 'update_time') return fmtTime(item?.[k])
  return item?.[k]
}

function labelOf(arr, value) {
  const f = (arr || []).find(i => i.dmm === (value ?? ''))
  return f?.dmmc || value || ''
}

function fmtTime(val) {
  if (!val) return ''
  try {
    const d = typeof val === 'string' ? new Date(val) : val
    if (isNaN(d)) return String(val)
    const y = d.getFullYear()
    const m = String(d.getMonth()+1).padStart(2,'0')
    const dd = String(d.getDate()).padStart(2,'0')
    const hh = String(d.getHours()).padStart(2,'0')
    const mm = String(d.getMinutes()).padStart(2,'0')
    const ss = String(d.getSeconds()).padStart(2,'0')
    return `${y}-${m}-${dd} ${hh}:${mm}:${ss}`
  } catch(e) {
    return String(val)
  }
}

function handleResize() { adjustHeaderGutter(); fitHeaderWidthsToTitles() }

onMounted(async () => {
  adjustHeaderGutter()
  await fitHeaderWidthsToTitles()
  await syncColWidths()
  // 监听窗口尺寸变化
  window.addEventListener('resize', handleResize)
  // 监听表格容器尺寸变化（更准确）
  try {
    // @ts-ignore
    resizeObserver = new ResizeObserver(() => { adjustHeaderGutter(); fitHeaderWidthsToTitles(); syncColWidths() })
    if (cmBodyRef.value) resizeObserver.observe(cmBodyRef.value)
  } catch {}
  // 等待页面资源与字体加载完成后再同步一次，避免字体替换引起的列宽变化
  window.addEventListener('load', () => { setTimeout(() => { fitHeaderWidthsToTitles(); syncColWidths() }, 0) })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  try { if (resizeObserver && cmBodyRef.value) resizeObserver.unobserve(cmBodyRef.value) } catch {}
  resizeObserver = null
})

function onPageSizeChange(e) {
  try {
    const val = Number((e && e.target && e.target.value) || 0)
    if (val) emits('update:page-size', val)
  } catch {}
}

// 数据变化后重新测量（排序/分页/筛选都会影响）
// 关闭自动同步时，不监听
if (enableAutoSync) {
  watch(() => sortedItems.value && sortedItems.value.length, () => { syncColWidths() })
  watch(() => keys && keys.length, () => { syncColWidths() })
}
// 不开启自动同步时，仍需在列集合变化时适配表头标题
watch(() => columns && columns.length, () => { fitHeaderWidthsToTitles() })
</script>

<style scoped>
.cm-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  table-layout: fixed !important;
}
.cm-table th,
.cm-table td { box-sizing: border-box; padding: 8px 12px; background: #fff; }
.cm-table thead th {
  background: #f9fafb;
  border-top: 1px solid var(--tq-border, #e5e7eb);
}
.cm-table thead th:first-child,
.cm-table tbody td:first-child {
  border-left: 1px solid var(--tq-border, #e5e7eb);
}
.cm-table .header-gutter {
  padding: 0;
  border-left: 0;
  border-right: 0;
  background: transparent;
}
/* 保证表头/表体第一列右边线一致 */
.cm-table thead th,
.cm-table tbody td {
  line-height: 1.5;
}

/* 冻结列样式（表头与表体一致） */
.freeze-head,
.freeze-cell { position: sticky; left: 0; z-index: 2; background: #fff; }
.freeze-head { z-index: 3; background: #f9fafb; }
/* 统一边框：用单边框+阴影模拟冻结列右边线，避免双线叠加 */
.cm-table tbody td { border-bottom: 1px solid var(--tq-border, #e5e7eb); border-right: 1px solid var(--tq-border, #e5e7eb); }
.cm-table thead th { border-top: 1px solid var(--tq-border, #e5e7eb); border-bottom: 1px solid var(--tq-border, #e5e7eb); border-right: 1px solid var(--tq-border, #e5e7eb); }
.cm-table thead th:first-child,
.cm-table tbody td:first-child { border-left: 1px solid var(--tq-border, #e5e7eb); }

/* 冻结列去掉自身右边框，改用阴影，确保表头与数据右边线重合 */
.cm-table .freeze-head,
.cm-table .freeze-cell { border-right: 0 !important; }
.cm-table .freeze-head::after,
.cm-table .freeze-cell::after {
  content: "";
  position: absolute;
  top: 0; bottom: 0; right: 0;
  width: 1px;
  background: var(--tq-border, #e5e7eb);
  pointer-events: none;
}

/* 表头内部容器不再额外贡献宽度，只用于布局 */
.th-inner,
.td-inner { padding: 0; margin: 0; width: 100%; box-sizing: border-box; }
.th-inner { display: flex; align-items: center; justify-content: space-between; gap: 6px; width: 100%; min-width: 0; }
.th-title { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 列宽拖拽手柄不占据布局宽度 */
.col-resizer {
  position: absolute;
  right: -3px; top: 0; bottom: 0;
  width: 6px;
  cursor: col-resize;
  z-index: 4;
}
.cm-table th { position: relative; overflow: hidden; }
.cm-table td { position: relative; }

/* 滚动容器样式（若项目已有同名类可与之合并） */
.cm-scroll-x { overflow-x: auto; overflow-y: hidden; }
.cm-body { overflow: auto; }

/* 固定头 + 滚动体 结构 */
.cm-table-fixed { 
  display: flex; flex-direction: column; width: 100%; min-height: 0; 
  background: #fff;
  border: 1px solid #e5e7eb; border-radius: 12px; padding: 12px; 
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  box-sizing: border-box;
}
.cm-scroll-x { position: sticky; top: 0; z-index: 10; background: transparent; border-bottom: 1px solid #e5e7eb; max-width: 100%; overflow-x: auto; overflow-y: hidden; }
.cm-head-inner { display: inline-block; min-height: 36px; height: 36px; background: transparent; }
.cm-head-inner table { height: 36px; }

.cm-body { 
  width: 100%; 
  max-width: 100%; 
  flex: 1 1 auto; 
  min-height: 0; 
  max-height: 100%; 
  overflow-x: auto; 
  overflow-y: auto; 
  -webkit-overflow-scrolling: touch; 
}

/* 表格样式，参考工单结果表 */
.cm-table { border-collapse: separate; border-spacing: 0; width: max-content; table-layout: fixed; font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif; font-size: 14px; color: #111827; }
.cm-table thead { position: sticky; top: 0; z-index: 2; background: #f5f7ff; }
.cm-table th, .cm-table td { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 400; font-size: 14px; }
.cm-table thead th { background: #f5f7ff; position: relative; color: #0b57d0; font-weight: 500; }

/* 冻结列占位（暂不接入逻辑，仅样式） */
.cm-table tbody .freeze-cell { position: sticky; background: #fff; z-index: 4; top: auto; }
.cm-table thead th.freeze-head { position: sticky; left: 0; background: #f5f7ff; z-index: 12; }

/* 表头操作区与图标 */
.cm-table .th-inner { display: flex; align-items: center; gap: 6px; padding-right: 0; }
.cm-table .th-title { flex: 1 1 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis; }
.cm-table .th-actions { position: static; transform: none; right: auto; top: auto; display: inline-flex; gap: 6px; flex: 0 0 auto; margin-right: 6px; z-index: 2; }
.cm-table .th-btn { width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; border: none; background: transparent; color: #64748b; cursor: pointer; padding: 0; }
.cm-table .th-btn:hover { color: #0b57d0; }
.cm-table .th-btn svg { width: 16px; height: 16px; }

/* 操作列宽度略窄 */
.op-col { width: 160px; }
/* 操作列按钮可见性与布局优化 */
.cm-table td.op-col { display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
.cm-table td.op-col .icon-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; padding: 0;
  border-radius: 6px; border: 1px solid #e5e7eb; background: #ffffff; color: #475569;
  cursor: pointer;
}
.cm-table td.op-col .icon-btn svg { width: 16px; height: 16px; }
.cm-table td.op-col .icon-btn:hover { background: #f8fafc; border-color: #cbd5e1; color: #0f172a; }

/* 分类配色，增强对比度 */
.cm-table td.op-col .icon-btn.info { color: #0b57d0; border-color: #93c5fd; background: #eff6ff; }
.cm-table td.op-col .icon-btn.info:hover { color: #0a46ab; border-color: #60a5fa; background: #dbeafe; }

.cm-table td.op-col .icon-btn.warn { color: #dc2626; border-color: #fecaca; background: #fff1f2; }
.cm-table td.op-col .icon-btn.warn:hover { color: #b91c1c; border-color: #fca5a5; background: #ffe4e6; }

.cm-table td.op-col .icon-btn.success { color: #16a34a; border-color: #bbf7d0; background: #f0fdf4; }
.cm-table td.op-col .icon-btn.success:hover { color: #15803d; border-color: #86efac; background: #dcfce7; }

/* 控制台：紫色系，提升可辨识度 */
.cm-table td.op-col .icon-btn.console { color: #7c3aed; border-color: #c4b5fd; background: #f5f3ff; }
.cm-table td.op-col .icon-btn.console:hover { color: #6d28d9; border-color: #a78bfa; background: #ede9fe; }

/* 滚动条外观 */
.cm-body { scrollbar-width: auto; }
.cm-body::-webkit-scrollbar { width: 10px; height: 10px; }
.cm-body::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 6px; }
.cm-body::-webkit-scrollbar-track { background: #f1f5f9; }
.cm-scroll-x { scrollbar-width: auto; }
.cm-scroll-x::-webkit-scrollbar { width: 0; height: 0; background: transparent; }

/* 统一分页样式（复用工单查询风格） */
.tq-pagination { display: flex; align-items: center; gap: 8px; width: 100%; margin-top: 10px; padding-top: 8px; text-align: left; flex: 0 0 auto; position: static; background: transparent; border-top: 1px solid #e5e7eb; }
.tq-pagination .muted { color: #64748b; }
.tq-pagination select { color: #0b57d0; font-weight: 400; font-size: 14px; height: 28px; }
</style>
