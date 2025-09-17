function onConnChange(ev: Event) {
  try {
    const val = (ev.target as HTMLSelectElement).value
    const id = /^\d+$/.test(val) ? Number(val) : val
    // 更新选中连接并刷新菜单树/数据库列表
    try { (state as any).selectedConnId = id } catch {}
    // 清空与上个连接相关的选择/展开/过滤
    try { state.selectedDbs = [] } catch {}
    try { (state as any).expandedDb = {} } catch {}
    try { state.filter = '' } catch {}
    try { state.tables = {} as any } catch {}
    try { state.selectedDb = '' as any } catch {}
    // 关闭下拉并重新加载数据库
    try { state.dbDropdownOpen = false } catch {}
    try { state.databases = [] as any } catch {}
    // 重新加载数据库列表
    try { (state as any).loadDatabases ? (state as any).loadDatabases() : null } catch {}
    // 若组合式未暴露 loadDatabases，则走 initConsole 兜底
    try { initConsole(id as any) } catch {}
  } catch {}
}
<template>
  <div class="dv-sql-console" :class="mode">
    <!-- 工具栏（与 App.vue 浮层结构保持一致的精简版本） -->
    <div class="card section-block tq-toolbar">
      <div class="tq-toolbar-row grid-12">
        <!-- 连接 2/12，左外边距 10px -->
        <div class="tq-col-2 tq-ml10">
          <label class="icon-label tq-conn" aria-label="连接">
            <span class="mi" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3.9 12a5 5 0 0 1 5-5h3v2h-3a3 3 0 1 0 0 6h3v2h-3a5 5 0 0 1-5-5Zm7.2 1h1.8v-2h-1.8v2Zm3-6h3a5 5 0 1 1 0 10h-3v-2h3a3 3 0 1 0 0-3h-3v-2Z"/></svg></span>
            <select class="tq-conn-select" :value="state.selectedConnId" @change="onConnChange($event)" title="请选择连接">
              <option v-for="c in (state.conns||[])" :key="'c-'+c.id" :value="c.id">
                {{ c.description || (c.ip+':' + c.port) || ('#'+c.id) }}
              </option>
            </select>
          </label>
        </div>
        <!-- 数据库 3/12，左外边距 20px（恢复左侧图标） -->
        <div class="tq-col-3 tq-ml20">
          <label class="icon-label tq-db" aria-label="数据库">
            <span class="mi" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                <ellipse cx="12" cy="6" rx="7" ry="3"></ellipse>
                <path d="M5 6v9c0 1.66 3.13 3 7 3s7-1.34 7-3V6"/>
                <path d="M5 9c0 1.66 3.13 3 7 3s7-1.34 7-3"/>
                <path d="M5 12c0 1.66 3.13 3 7 3s7-1.34 7-3"/>
              </svg>
            </span>
            <div class="tq-db-multi" :class="{ disabled: !state.selectedConnId }">
              <div ref="dbSummaryRef" class="tq-db-summary" :title="state.selectedDbs.length ? state.selectedDbs.join(', ') : '请选择数据库'" @click="toggleDbDropdown" :aria-expanded="state.dbDropdownOpen">
                <span class="placeholder" v-if="!state.selectedDbs.length">请选择数据库</span>
                <template v-else>
                  <span class="tag">{{ state.selectedDbs[0] }}</span>
                  <span v-if="state.selectedDbs.length>1" class="more">+{{ state.selectedDbs.length-1 }}</span>
                </template>
                <span class="caret">▾</span>
              </div>
              <div v-if="state.dbDropdownOpen" class="tq-db-overlay" @mousedown="state.dbDropdownOpen=false" aria-hidden="true"></div>
              <div v-if="state.dbDropdownOpen" ref="dbPanelRef" class="tq-db-panel" :style="{ width: (dbPanelWidth||240) + 'px' }" @mousedown.stop @mouseup.stop @pointerdown.stop @pointerup.stop @pointermove.stop @wheel.stop @click.stop>
                <div class="tq-db-search-wrap">
                  <input class="tq-db-search" v-model="state.filter" placeholder="搜索数据库..." @wheel.stop @mousedown.stop @mouseup.stop @click.stop />
                  <button type="button" class="tq-db-clear" title="清空选择" @click.stop="clearDbSelection" aria-label="清空选择" role="button">×</button>
                </div>
                <div class="tq-db-list" :style="{ '--db-name-col-width': (dbNameColWidth || 0) + 'px' }" @mousedown.stop @mouseup.stop @pointerdown.stop @pointerup.stop @pointermove.stop @wheel.stop @click.stop>
                  <label v-for="db in filteredDatabases" :key="'opt-'+db" class="opt"
                         :class="{ selected: state.selectedDbs.includes(db) }"
                         :title="db" role="button" :aria-pressed="state.selectedDbs.includes(db)"
                         @click.stop="onDbToggle(db, !state.selectedDbs.includes(db))">
                    <span class="txt">{{ db }}</span>
                  </label>
                </div>
              </div>
            </div>
          </label>
        </div>
        <!-- 过滤 3/12，左外边距 0px -->
        <div class="tq-col-3">
          <label class="icon-label tq-filter" aria-label="过滤">
            <span class="mi" aria-hidden="true"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 5h18v2l-7 7v4l-4 2v-7L3 5Z"/></svg></span>
            <input v-model="state.filter" placeholder="过滤表名，支持模糊匹配" />
          </label>
        </div>
        <!-- 按钮组 4/12，右对齐，右外边距 10px -->
        <div class="tq-col-4 tq-actions right tq-mr10">
          <button class="icon-btn add" title="执行 (Ctrl+Enter)" @click="executeSQL" :disabled="state.running || !state.sql.trim()">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          </button>
          <button class="icon-btn warn" title="停止" @click="stopExecution" :disabled="!state.running">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h12v12H6z"/></svg>
          </button>
          <button class="icon-btn info" title="美化SQL" @click="beautifySQL" :disabled="!state.sql.trim()">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z"/></svg>
          </button>
          <button class="icon-btn" title="查看执行计划" @click="viewPlan" :disabled="!state.sql.trim()">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zM3 9h2V7H3v2zm4 8h2v-6H7v6zm4 0h2V5h-2v12zm4 0h2v-8h-2v8zm4 0h2v-4h-2v4z"/></svg>
          </button>
          <button class="icon-btn" title="导出 CSV" @click="exportCSV" :disabled="!(state.result && state.result.type==='table')">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7H3l9-9 9 9h-2Zm-7 7h2v-6h-2v6Z"/></svg>
          </button>
          <button class="icon-btn" title="导出 Excel" @click="exportExcel" :disabled="!(state.result && state.result.type==='table')">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 4h9a1 1 0 0 1 1 1v3h6v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1Zm9 5V6H5v12h14V9h-6Zm-6.5 7 2.75-4L6.5 8h2.3l1.55 2.6L11.9 8h2.3l-2.75 4 2.75 4h-2.3l-1.55-2.6L8.8 16H6.5Z"/></svg>
          </button>
          <!-- 在新窗口打开（轻量跳转） -->
          <button class="icon-btn" title="在新窗口打开" @click="openInNewWindow">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M14 3h7v7h-2V6.41l-9.29 9.3-1.42-1.42 9.3-9.29H14V3ZM5 5h7v2H7v10h10v-5h2v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z"/></svg>
          </button>
        </div>
      </div>
    </div>
    <!-- 头部（可选）由父级决定，Shell 专注于核心控制台区域 -->
    <div class="tq-main" :class="{ 'left-collapsed': state.leftCollapsed }">
        <div class="tq-left col-span-2">
          <!-- 树形结构 -->
          <div class="tq-tree" role="tree" @wheel.passive="onTreeWheel">
            <div class="tq-tree-db"
                 v-for="db in state.databases"
                 :key="'db-'+db"
                 v-show="(!state.filter || db.includes(state.filter)) && (!(state.forceTreeFilter && state.selectedDbs && state.selectedDbs.length>=1) || state.selectedDbs.includes(db))">
              <div class="tq-tree-db-name" @click="toggleDbExpand(db)">
                <span class="arrow" :class="{open: state.expandedDb && state.expandedDb[db]}" aria-hidden="true">›</span>
                <span>{{ db }}</span>
              </div>
              <ul v-show="state.expandedDb && state.expandedDb[db]" class="tq-tree-tables">
                <li v-for="tbl in filteredTables(db)" :key="'t-'+db+'-'+tbl" @click="appendTableToSQL(db, tbl)">
                  {{ tbl }}
                </li>
                <li v-if="state.tablesLoading && state.tablesLoading[db]" class="muted">加载中...</li>
                <li v-if="!(state.tablesLoading && state.tablesLoading[db]) && (!state.tables[db] || state.tables[db].length===0)" class="muted">无表</li>
              </ul>
            </div>
          </div>
        </div>
        <!-- 左栏折叠/展开按钮（绝对定位于 .tq-main 内） -->
        <button class="tq-left-toggle" :class="{ collapsed: state.leftCollapsed }" @click="toggleLeftCollapsed" title="折叠/展开侧栏" aria-label="折叠/展开侧栏">
          <span class="chev">{{ state.leftCollapsed ? '›' : '‹' }}</span>
        </button>
        <div class="tq-right col-span-10" ref="rightRef">
          <!-- 紧凑型标签栏 -->
          <SqlTabs />
          <!-- 编辑器区域 -->
          <div class="tq-editor-wrap" :style="{ height: (state.editorHeight || 220) + 'px' }">
            <SqlEditor />
        </div>
        <div class="tq-vsplit" title="拖动调整编辑器高度"></div>
        <!-- 结果区 -->
        <div class="tq-result">
          <div class="tq-result-body">
            <template v-if="state.result && state.result.type==='table'">
              <div class="tq-result-scroll" ref="tqBodyRef" @scroll="onBodyScroll">
                <ResultTable />
              </div>
            </template>
            <template v-else-if="state.result && state.result.type==='text'">
              <pre class="tq-text">{{ (state.result as any).text }}</pre>
            </template>
            <template v-else>
              <div class="muted">在此显示查询结果或执行信息</div>
            </template>
          </div>
          <!-- 固定底部横向滚动条，避免需要先把竖向滚动条拉到底才出现 -->
          <div class="tq-x-scroll" ref="tqScrollXRef" @scroll="onXScroll" v-show="state.result && state.result.type==='table'"><div class="spacer" :style="{ width: (state.bodyTableWidth || 1200) + 'px', height: '1px' }"></div></div>
          <!-- 分页条：固定在结果区底部，始终可见 -->
          <div class="tq-pagination" v-if="state.result && state.result.type==='table'">
            <button class="icon-btn" :disabled="state.page<=1" @click="goToPage(state.page-1)" title="上一页">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15.41 7.41 14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
            </button>
            <span class="muted">第</span>
            <input type="number" v-model.number="pageInput" @keyup.enter="handlePageJump" min="1" :max="totalPages" style="width:70px;height:28px" />
            <span class="muted">/ {{ totalPages }} 页</span>
            <button class="icon-btn" :disabled="state.page>=totalPages" @click="goToPage(state.page+1)" title="下一页">
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M8.59 16.59 13.17 12 8.59 7.41 10 6l6 6-6 6z"/></svg>
            </button>
            <span class="muted" style="margin-left:12px">每页</span>
            <select :value="state.pageSize" @change="handlePageSizeChange($event)" title="每页条数">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span class="muted">条，共 {{ state.totalRows || 0 }} 条</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, computed, provide, nextTick } from 'vue'
import { useSqlConsole } from './useSqlConsole'
import ResultTable from './ResultTable.vue'
import SqlTabs from './SqlTabs.vue'
import SqlEditor from './SqlEditor.vue'

interface Props {
  initConnId?: number | string
  initDb?: string
  initSql?: string
  mode?: 'modal' | 'page'
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'modal'
})

// 轻量打开新窗口：仅携带一次性参数，互不同步
function openInNewWindow() {
  try {
    const base = '/db-console.html'
    const params = new URLSearchParams()
    if (state.selectedConnId != null && String(state.selectedConnId).trim() !== '') {
      params.set('connId', String(state.selectedConnId))
    }
    if (state.selectedDb) params.set('database', state.selectedDb)
    if (state.sql && state.sql.trim()) params.set('sql', encodeURIComponent(state.sql))
    const url = `${base}?${params.toString()}`
    window.open(url, '_blank', 'noopener')
  } catch {}
}

const {
  state,
  filteredDatabases,
  filteredTables,
  appendTableToSQL,
  initConsole,
  executeSQL,
  stopExecution,
  beautifySQL,
  viewPlan,
  ensureSqlEditor,
  toggleDbDropdown,
  onDbToggle,
  clearDbSelection,
  totalPages,
  goToPage,
  toggleLeftCollapsed,
  exportCSV,
  exportExcel,
  loadTables,
  // tabs api from composable
  newQueryTab,
  closeQueryTab,
  setActiveTab,
} = useSqlConsole()
const rightRef = ref<HTMLElement | null>(null)
const pageInput = ref<number | null>(null)
const dbPanelRef = ref<HTMLElement | null>(null)
const dbSummaryRef = ref<HTMLElement | null>(null)
const dbPanelWidth = ref<number>(240)
// 用于对齐每行文本列宽，让所有行的选中标记/后续图标对齐
const dbNameColWidth = ref<number>(0)


function toggleDbExpand(db: string) {
  if (!state.expandedDb) (state as any).expandedDb = {}
  ;(state as any).expandedDb[db] = !(state as any).expandedDb[db]
  // 选择活动库并按需加载表
  try { state.selectedDb = db } catch {}
  try { if (!state.tables[db]) loadTables(db) } catch {}
}

// 只读连接标签（与 App.vue 中 consoleConnLabel 逻辑等价的简化版）
const connLabel = computed(() => {
  try {
    const arr = Array.isArray(state.conns) ? state.conns : []
    const idNum = typeof state.selectedConnId === 'string' ? Number(state.selectedConnId) : state.selectedConnId
    const c = arr.find((x: any) => x.id === idNum)
    if (!c) return `#${state.selectedConnId ?? ''}`
    return c.description || `${c.ip}:${c.port}` || `#${c.id}`
  } catch { return `#${state.selectedConnId ?? ''}` }
})

onMounted(async () => {
  if (props.initConnId != null) {
    await initConsole(props.initConnId)
  }
  // 一次性应用初始库与初始 SQL（若提供）
  try {
    if (props.initDb) {
      state.selectedDb = props.initDb
      if (props.initConnId) try { await loadTables(props.initDb) } catch {}
    }
  } catch {}
  try {
    if (props.initSql) {
      state.sql = props.initSql
    }
  } catch {}
  // 栅格布局，无需动态测量宽度
  pageInput.value = (state.page as unknown as number) || 1
  // 若无标签，创建一个默认标签，避免仅出现“+”
  try { if (!state.qTabs || state.qTabs.length === 0) newQueryTab() } catch {}
  // 初始化编辑器（独立页 contenteditable 版本）
  try { await ensureSqlEditor(tqCodeRef.value as any) } catch {}
  // 文档点击：点击外部关闭 DB 下拉
  document.addEventListener('mousedown', onDocClickCloseDb, true)
})

watch(() => state.page, (p) => {
  pageInput.value = (p as unknown as number) || 1
})

// 结果变化后，计算列宽与容器宽度
watch(() => state.result, async () => {
  await nextTick()
  try { computeColWidths() } catch {}
})

// 打开 DB 下拉时：锁定面板宽度为触发器等宽，滚动时不再变化；并计算最长库名列宽以便行内对齐
watch(() => state.dbDropdownOpen, async (open) => {
  if (!open) return
  await nextTick()
  try {
    const triggerW = (dbSummaryRef.value?.clientWidth || 240)
    dbPanelWidth.value = Math.max(200, Math.floor(triggerW))
    // 计算最长库名像素宽度
    let list: string[] = []
    try {
      const arr = Array.isArray(state.databases) ? state.databases : []
      list = arr.filter((s: any) => typeof s === 'string') as string[]
    } catch {}
    const canvas = document.createElement('canvas')
    const ctx2d = canvas.getContext('2d')
    let maxText = 0
    if (ctx2d) {
      // 与列表字体一致
      ctx2d.font = '14px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif'
      for (const s of list) {
        const m = ctx2d.measureText(s)
        maxText = Math.max(maxText, Math.ceil(m.width))
      }
    } else {
      for (const s of list) maxText = Math.max(maxText, s.length * 8)
    }
    // 左侧对勾占位 16px + 文本左右内边距 8px
    dbNameColWidth.value = Math.max(80, maxText + 16 + 8)
  } catch {}
})

// 程序修改 state.sql 时，同步到 contenteditable
const activeTab = computed(() => (state.qTabs || []).find(t => t.id === state.activeQueryTabId) || null)
watch(() => activeTab.value?.sql, (val) => {
  const el = tqCodeRef.value as HTMLElement | null
  if (!el) return
  const cur = el.textContent || ''
  if (val !== cur) el.textContent = val || ''
})

// ---- 向子组件提供 tqCtx，兼容 SqlTabs / SqlEditor / ResultTable ---
// DOM refs（由子组件挂载后回填）
const tqEditorRef = ref<HTMLElement | null>(null)
const tqCodeRef = ref<HTMLElement | null>(null)
const tqHeadTableRef = ref<HTMLElement | null>(null)
const tqBodyTableRef = ref<HTMLElement | null>(null)
const tqScrollXRef = ref<HTMLElement | null>(null)
const tqBodyRef = ref<HTMLElement | null>(null)

// 激活标签：走组合式方法，并在切换后同步编辑器内容
function activateQueryTab(id: string) {
  try { setActiveTab(id) } catch { state.activeQueryTabId = id }
  nextTick(() => { try { ensureSqlEditor(tqCodeRef.value as any) } catch {} })
}

// 结果表的简单实现/占位：展示当前页数据
function getDisplayedRows() {
  try {
    if (!(state.result && (state.result as any).rows)) return []
    const rows = (state.result as any).rows || []
    const p = Number(state.page) || 1
    const ps = Number(state.pageSize) || 50
    const start = (p - 1) * ps
    return rows.slice(start, start + ps)
  } catch { return [] }
}

function headerLockClick(i: number) {
  // 简化：点击 i 列即将冻结数设置为 i+1；再次点击同一列则取消到 0
  if (state.freezeCount === i + 1) state.freezeCount = 0
  else state.freezeCount = i + 1
}
function toggleSort(col: string) {
  const key = col
  if (state.sortKey !== key) { state.sortKey = key; state.sortDir = 'asc' }
  else if (state.sortDir === 'asc') state.sortDir = 'desc'
  else if (state.sortDir === 'desc') { state.sortKey = ''; state.sortDir = '' }
  else state.sortDir = 'asc'
}
function startColResize(i: number) { /* 占位 */ }
function onBodyScroll() {
  try {
    const body = getBodyScrollEl()
    const head = getHeadScrollEl()
    const xs = tqScrollXRef.value as HTMLElement | null
    const sl = body?.scrollLeft || 0
    if (head) head.scrollLeft = sl
    if (xs && xs.scrollLeft !== sl) xs.scrollLeft = sl
  } catch {}
}

function onXScroll() {
  try {
    const xs = tqScrollXRef.value as HTMLElement | null
    const body = getBodyScrollEl()
    const head = getHeadScrollEl()
    const sl = xs?.scrollLeft || 0
    if (body && body.scrollLeft !== sl) body.scrollLeft = sl
    if (head && head.scrollLeft !== sl) head.scrollLeft = sl
  } catch {}
}

function getBodyScrollEl(): HTMLElement | null {
  // 优先使用子组件回填的 ref，否则在结果区内探测最大可横向滚动的容器作为 body
  const el = (tqBodyTableRef.value as HTMLElement | null) || (tqBodyRef.value as HTMLElement | null)
  if (el && el.scrollWidth > el.clientWidth) return el
  const root = tqBodyRef.value as HTMLElement | null
  if (!root) return null
  const candidates = Array.from(root.querySelectorAll('*')) as HTMLElement[]
  let best: HTMLElement | null = null
  for (const c of candidates) {
    const cs = getComputedStyle(c)
    if ((cs.overflowX === 'auto' || cs.overflowX === 'scroll') && c.scrollWidth > c.clientWidth) {
      if (!best || c.clientHeight > best.clientHeight) best = c
    }
  }
  return best
}

function getHeadScrollEl(): HTMLElement | null {
  // 优先 ref；否则在结果区中查找最可能的表头滚动容器（较矮且可横向滚动）
  const el = tqHeadTableRef.value as HTMLElement | null
  if (el && el.scrollWidth > el.clientWidth) return el
  const root = tqBodyRef.value as HTMLElement | null
  if (!root) return null
  const candidates = Array.from(root.querySelectorAll('*')) as HTMLElement[]
  let best: HTMLElement | null = null
  for (const c of candidates) {
    const cs = getComputedStyle(c)
    if ((cs.overflowX === 'auto' || cs.overflowX === 'scroll') && c.scrollWidth > c.clientWidth) {
      if (!best || c.clientHeight < best.clientHeight) best = c
    }
  }
  return best
}
function computeColWidths() {
  try {
    const res: any = state.result
    if (!(res && res.type === 'table' && Array.isArray(res.columns))) return
    const cols: string[] = res.columns
    // 基础列宽：均分容器或按最小宽度 120px 计算
    const container = rightRef.value as HTMLElement | null
    const containerWidth = Math.max(300, (container?.clientWidth || 800) - 24)
    const minCol = 180
    const sumMin = minCol * cols.length
    let bodyWidth = Math.max(containerWidth, sumMin)
    const even = Math.floor(bodyWidth / Math.max(1, cols.length))
    state.tableColWidths = cols.map(() => Math.max(minCol, even))
    state.bodyTableWidth = bodyWidth
  } catch {}
}
function adjustHeaderGutter() { /* 占位 */ }
function startResize() { /* 占位：编辑器高度拖拽在 Shell 外实现 */ }
async function onSqlHostClick() {
  try {
    await ensureSqlEditor(tqCodeRef.value as any)
    const el = tqCodeRef.value as HTMLElement | null
    if (el) el.focus()
  } catch {}
}

function onDocClickCloseDb(ev: MouseEvent) {
  try {
    // 不再在任意 mousedown 时动态调整面板宽度，避免点击横向滚动条导致面板突变
    const p = dbPanelRef.value
    const s = dbSummaryRef.value
    const t = ev.target as Node
    if (p && p.contains(t)) return
    if (s && s.contains(t)) return
    state.dbDropdownOpen = false
  } catch {}
}

onBeforeUnmount(() => {
  try { document.removeEventListener('mousedown', onDocClickCloseDb, true) } catch {}
  // 无需事件解绑
})

function onTreeWheel(ev: WheelEvent) {
  try {
    const el = ev.currentTarget as HTMLElement
    if (!el) return
    el.scrollTop += ev.deltaY
  } catch {}
}

function onDbToggleEvent(db: string, ev: Event) {
  try {
    const checked = (ev.target as HTMLInputElement).checked
    onDbToggle(db, checked)
  } catch {}
}

// 始终保持菜单默认折叠：页面初始与库列表变化时都收起
onMounted(() => {
  try { (state as any).expandedDb = {} } catch {}
})
watch(() => state.databases, () => {
  try { (state as any).expandedDb = {} } catch {}
})
watch(() => state.selectedConnId, () => {
  try { (state as any).expandedDb = {} } catch {}
})
watch(() => state.selectedDbs && state.selectedDbs.join(','), () => {
  try { (state as any).expandedDb = {} } catch {}
})

// ---- 分页交互 ----
async function handlePageJump() {
  const p = Number(pageInput.value || 1)
  if (!Number.isFinite(p)) return
  await goToPage(Math.max(1, Math.min(totalPages.value, p)))
}

async function handlePageSizeChange(ev: Event) {
  try {
    const val = Number((ev.target as HTMLSelectElement).value)
    if (!val || val === state.pageSize) return
    state.pageSize = val
    await goToPage(1)
  } catch {}
}

provide('tqCtx', {
  tq: state,
  // refs
  tqEditorRef,
  tqCodeRef,
  tqHeadTableRef,
  tqBodyTableRef,
  tqScrollXRef,
  tqBodyRef,
  // tab ops
  newQueryTab,
  activateQueryTab,
  closeQueryTab,
  // editor ops
  startResize,
  onSqlHostClick,
  // table ops
  headerLockClick,
  toggleSort,
  startColResize,
  onBodyScroll,
  getDisplayedRows,
  computeColWidths,
  adjustHeaderGutter,
})
</script>

<style scoped>
.dv-sql-console { height: 100vh; display: flex; flex-direction: column; }
.card.section-block.tq-toolbar { flex: 0 0 auto; }
/* 顶部与内容之间的留白，贴近工单查询 */
.tq-main { margin-top: 8px; }
.tq-main { flex: 1 1 auto; min-height: 0; height: auto; display: grid; grid-template-columns: repeat(12, 1fr); grid-template-rows: 1fr; gap: 0; padding: 0; background: #f8fafc; position: relative; }
.tq-main.left-collapsed { grid-template-columns: 0 repeat(11, 1fr); }
/* 左树作为滚动宿主，父容器不滚动 */
.tq-left { grid-column: 1; background: #f8fafc; border-right: 1px solid #e5e7eb; height: 100%; display: flex; flex-direction: column; overflow: hidden; min-height: 0; position: relative; z-index: 50; pointer-events: auto; box-sizing: border-box; }
.tq-main.left-collapsed .tq-left { display: none !important; border-right: none !important; }
.tq-main.left-collapsed .tq-right { grid-column: 1 / -1 !important; }
.tq-tree { padding: 8px; flex: 1 1 auto; min-height: 0; overflow: auto; scrollbar-width: thin; font-size:14px; }
.tq-tree::-webkit-scrollbar { width: 10px; height: 10px; }
.tq-tree::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 6px; }
.tq-tree::-webkit-scrollbar-thumb:hover { background: #64748b; }
.tq-tree-db-name { display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 4px 10px; border-radius: 6px; line-height: 28px; color:#0b57d0; font-weight: 400; }
.tq-tree-db-name:hover { background: #eef2ff; }
.tq-tree-tables { list-style: none; padding-left: 16px; margin: 4px 0 8px; font-size:14px; }
.tq-tree-tables li { line-height: 28px; padding: 2px 10px; border-radius: 4px; color:#334155; }
.tq-tree-tables li:hover { background:#f2f6ff; }
.tq-tree-db-name .arrow { display: inline-block; width: 10px; transform: rotate(90deg); transition: transform .15s; color:#64748b; font-size:12px; }
.tq-right { grid-column: 2; display: flex; flex-direction: column; height: 100%; min-height: 0; min-width: 0; z-index: 10; }
.tq-editor-wrap { background: #fff; border-bottom: 1px solid #e5e7eb; display: flex; align-items: stretch; justify-content: flex-start; color: #64748b; width: 100%; }
.tq-editor-wrap > * { width: 100%; max-width: none; }
.tq-editor-wrap :deep(.tq-sql),
.tq-editor-wrap :deep(.cm-editor) { width: 100% !important; }
.tq-editor-placeholder { padding: 24px; font-size: 14px; }
.tq-result { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.tq-result-body { flex: 1 1 auto; min-height: 0; overflow: hidden; padding: 12px; }
.tq-result-scroll { width: 100%; height: 100%; overflow-y: auto; overflow-x: hidden; }
.tq-x-scroll { flex: 0 0 auto; height: 14px; overflow-x: auto; overflow-y: hidden; border-top: 1px solid #e5e7eb; background: #fff; }
.tq-x-scroll .spacer { height: 1px; }
.tq-pagination { flex: 0 0 auto; display: flex; align-items: center; gap: 12px; padding: 8px 12px; border-top: 1px solid #e5e7eb; background: #fff; color:#374151; }
.tq-pagination .muted { color: #64748b; }
/* 左右翻页按钮：与工单查询一致的圆角、尺寸与配色 */
.tq-pagination .icon-btn { width: 28px; height: 28px; border-radius: 10px; border-color: #e5e7eb; background: #fff; color:#0b57d0; }
.tq-pagination .icon-btn:hover { background:#f8fafc; }
/* 页码输入框：圆角、边框与高度统一 */
.tq-pagination input[type="number"] { height: 28px; line-height: 28px; border:1px solid #e5e7eb; border-radius: 8px; padding: 2px 8px; box-sizing: border-box; color:#111827; }
/* 每页下拉：圆角、边框与高度统一 */
.tq-pagination select { height: 28px; border:1px solid #e5e7eb; border-radius: 8px; padding: 2px 28px 2px 8px; color:#111827; }
.tq-text { white-space: pre-wrap; font-family: Consolas, Monaco, monospace; }

/* ---- 12-column grid utilities ---- */
.grid-12 { display: grid; grid-template-columns: repeat(12, 1fr); gap: 8px; align-items: center; }
.tq-col-1 { grid-column: span 1; }
.tq-col-2 { grid-column: span 2; }
.tq-col-3 { grid-column: span 3; }
.tq-col-5 { grid-column: span 5; }
.tq-col-4 { grid-column: span 4; }
.tq-col-6 { grid-column: span 6; }
.col-span-2 { grid-column: span 2; }
.col-span-10 { grid-column: span 10; }
.tq-actions.right { display: flex; gap: 8px; justify-content: flex-end; justify-self: end; width: 100%; flex-wrap: nowrap; }
/* 按钮组小一号，仅作用于工具栏按钮，不影响分页等其他按钮 */
.tq-actions.right .icon-btn { width: 32px; height: 32px; }
.tq-actions.right .icon-btn svg { width: 18px; height: 18px; }

/* toolbar spacing utilities per spec */
.tq-ml10 { margin: 0; margin-left: 10px; }
.tq-ml20 { margin: 0; margin-left: 20px; }
.tq-mr10 { margin: 0; margin-right: 10px; }

/* ensure inner controls fill their grid cell */
.tq-col-2 .icon-label,
.tq-col-3 .icon-label { width: 100%; }
.tq-col-3 .tq-db-multi,
.tq-col-3 .tq-filter { width: 100%; }

/* 表头列名显示不全：取消强制截断，最小宽度在 computeColWidths 控制（对齐工单查询） */
:deep(.result-table th), :deep(.result-table td) { white-space: nowrap; }
:deep(.result-table th .cell), :deep(.result-table td .cell) { display: inline-block; max-width: none; overflow: visible; text-overflow: clip; }
/* 隐藏内部横向滚动条，仅保留下方固定横向滚动条 */
:deep(.result-table ::-webkit-scrollbar:horizontal) { height: 0 !important; }
:deep(.result-table) { scrollbar-gutter: stable both-edges; }
.muted { color: #9ca3af; }

/* 防止某些浏览器/全局样式把 SVG 放大，统一在本组件内约束 */
.dv-sql-console svg { width: 18px; height: 18px; display: inline-block; }

/* ---- toolbar & icons (subset from App.vue to keep identical look) ---- */
.card.section-block.tq-toolbar { padding: 8px 12px; border-bottom: 1px solid #e5e7eb; background: #fff; }
.tq-toolbar-row { gap: 8px; align-items: center; }
.tq-toolbar-row.grid-12 { display: grid !important; grid-template-columns: repeat(12, 1fr); }
/* 让控件在常规宽度下一行排布，高度/内边距统一 */
.tq-toolbar-row > .icon-label { flex: 0 0 auto; }
.icon-label { display: inline-flex; align-items: center; gap: 6px; }
/* 连接图标按钮：完全对齐工单查询 */
.icon-label .mi { width: 18px; height: 18px; display: inline-flex; align-items: center; justify-content: center; border: none; background: transparent; border-radius: 0; color: #3b82f6; opacity: 0.9; }
.icon-label .mi svg { width: 18px; height: 18px; display: block; }
/* 让数据库图标与工单查询保持细线风格 */
.tq-db .mi svg { fill: none; stroke: currentColor; stroke-width: 1.75; stroke-linecap: round; stroke-linejoin: round; }
/* 连接下拉选择器（与工单一致） */
.tq-conn-select { color:#0b57d0; font-size:14px; line-height:22px; height:32px; padding:4px 8px; border:1px solid #c7d2fe; border-radius:6px; background:#fff; box-sizing:border-box; width: 100%; }
/* 连接展示：样式对齐工单查询的下拉选择器（但维持只读） */
.tq-conn-readonly { min-width: 220px; max-width: 36vw; height: 32px; display: inline-flex; align-items: center; padding: 4px 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; background:#fff; border:1px solid #c7d2fe; border-radius: 6px; box-shadow: none; color:#0b57d0; }
.tq-db-multi { position: relative; min-width: 240px; }
.tq-db-multi.disabled { opacity: .6; pointer-events: none; }
.tq-db-summary { display:flex; align-items:center; gap:6px; min-width: 200px; max-width: 260px; width:100%; height: 32px; padding: 4px 8px; border: 1px solid #c7d2fe; border-radius: 6px; background: #fff; cursor: pointer; color:#0b57d0; box-sizing:border-box; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; font-size:14px; line-height:22px; }
.tq-db-summary .tag { background:#eef2ff; color:#0b57d0; padding:2px 6px; border-radius: 4px; }
.tq-db-summary .caret { margin-left: auto; color:#64748b; font-size: 12px; }
.tq-db-overlay { position: fixed; inset: 0; background: transparent; }
.tq-db-panel { position: absolute; top: 40px; left: 0; z-index: 200; max-width: 88vw; max-height: 50vh; overflow-x: hidden; overflow-y: auto; background: #fff; border:1px solid #e5e7eb; border-radius: 10px; padding: 8px; margin-top: 4px; box-shadow: 0 6px 20px rgba(17,24,39,.08); width: v-bind(dbPanelWidth); }
.tq-db-search-wrap { display:flex; align-items:center; gap:6px; padding-bottom: 6px; border-bottom:1px solid #f1f5f9; margin-bottom: 6px; }
.tq-db-search { flex:1 1 auto; height:32px; padding: 4px 8px; border:1px solid #c7d2fe; border-radius: 6px; box-sizing: border-box; color:#0b57d0; font-size:14px; }
.tq-db-clear { background: transparent; border:none; color:#6b7280; cursor:pointer; font-size:16px; line-height:1; }
.tq-db-list { display:block; max-height: 40vh; overflow-y:auto; overflow-x:auto; padding: 4px 2px; }
.tq-db-list .opt { display:flex; align-items:center; justify-content: flex-start; gap:8px; min-height:32px; height:32px; padding:4px 8px; border:none; border-radius:6px; background:transparent; cursor:pointer; min-width:max-content; width:auto; box-sizing:border-box; overflow:visible; white-space:nowrap; font-size:14px; }
.tq-db-list .opt .txt { position: relative; line-height: 1; flex: 1 1 auto; min-width: max-content; overflow: visible; padding-left: 16px; }
.tq-db-list .opt .opt-check { flex: 0 0 auto; margin-left: 8px; }
.tq-db-list .opt.selected { background:#eef2ff; color:#0b57d0; }
.tq-db-list .opt.selected .txt::before { content: '✓'; position: absolute; left: 0; top: 50%; transform: translateY(-50%); color:#0b57d0; font-weight: 700; font-size: 12px; }
.tq-filter input { height: 32px; padding: 4px 8px; border:1px solid #c7d2fe; border-radius: 6px; box-sizing: border-box; color:#0b57d0; font-size:14px; width: 100%; min-width: 200px; max-width: 260px; }
.icon-btn { display:inline-flex; align-items:center; justify-content:center; width:36px; height:36px; border:1px solid #d1d5db; border-radius:6px; background:#fff; color:#374151; cursor:pointer; }
.icon-btn svg { width: 22px; height: 22px; padding: 2px; box-sizing: content-box; }
.icon-btn.add { background:#e8f0fe; border-color:#3b82f6; color:#0b57d0; }
.icon-btn.warn { background:#fff1f2; border-color:#fecaca; color:#b91c1c; }
.icon-btn.info { background:#e6f0ff; border-color:#c7d2fe; color:#0b57d0; }

/* left toggle */
.tq-left-toggle { position: absolute; z-index: 999; top: 50%; left: calc((100% / 12) * 2); transform: translate(-50%, -50%); width: 16px; height: 36px; display: inline-flex; align-items: center; justify-content: center; border: 1px solid #94a3b8; border-left: none; background: #f1f5f9; cursor: pointer; border-radius: 0 8px 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,.10); }
.tq-main.left-collapsed .tq-left-toggle { left: 0; transform: translate(0, -50%); border-left: 1px solid #cbd5e1; border-right: none; border-radius: 8px 0 0 8px; }
.tq-left-toggle .chev { display:block; padding: 0 2px; color:#0f172a; line-height: 1; font-weight: 700; font-size: 12px; }
.tq-left-toggle:hover { background:#f8fafc; }

/* vertical splitter mimics App.vue */
.tq-vsplit { height: 8px; cursor: row-resize; background: linear-gradient(to bottom, transparent 0, transparent 3px, #e5e7eb 3px, #e5e7eb 4px, transparent 4px, transparent 100%); }
</style>
