<template>
  <div class="dv-sql-console" :class="mode">
    <!-- 页面模式显示标题：控制台 [user@ip:port] -->
    <div v-if="mode==='page'" class="tq-title">
      <span class="t">控制台</span>
      <span class="i">[{{ connLabel }}]</span>
    </div>
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
          <!-- 回主页面打开浮动控制台（仅页面模式显示） -->
          <button v-if="mode==='page'" class="icon-btn" title="回主页面打开浮动控制台" @click="openInOpener">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8h5z"/></svg>
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
          <!-- 紧凑型标签栏（固定首帧高度，避免字体/图标加载导致跳动） -->
          <div class="tq-tabs-wrap">
            <SqlTabs />
          </div>
          <!-- 编辑器区域 -->
          <div class="tq-editor-wrap" :style="{ height: Math.max(0, Number(state.editorHeight || 0) || 0) + 'px' }">
            <SqlEditor />
        </div>
        <div class="tq-vsplit" title="拖动调整编辑器高度" @mousedown="startResize"></div>
        <!-- 结果区 -->
        <div class="tq-result">
          <div class="tq-result-body">
            <!-- 执行中状态提示（仅独立页显示，避免影响浮动窗口） -->
            <div v-if="mode==='page' && state.running" class="tq-executing" aria-live="polite">
              <span class="spinner" aria-hidden="true"></span>
              执行中...
            </div>
            <template v-if="state.result && state.result.type==='table'">
              <div class="tq-result-scroll" ref="tqBodyRef" @scroll="onBodyScroll">
                <ResultTable :key="`${state.page}|${state.pageSize}|${(state.result && state.result.rows && state.result.rows.length) || 0}`" />
              </div>
            </template>
            <template v-else-if="state.result && state.result.type==='text' && !(state.running && String((state.result as any).text||'').includes('执行中'))">
              <pre class="tq-text">{{ (state.result as any).text }}</pre>
            </template>
            <template v-else-if="!state.running">
              <div class="muted">在此显示查询结果或执行信息</div>
            </template>
          </div>
          <!-- 固定底部横向滚动条（自定义轨道+拇指），仅作为 UI 控件，不使用原生横滚 -->
          <div class="tq-x-scroll" ref="tqScrollXRef" v-show="state.result && state.result.type==='table'">
            <div class="x-track" ref="tqXTrackRef" @pointerdown="onXTrackPointer" @wheel.prevent="onXWheel">
              <div class="x-thumb" ref="tqXThumbRef" @pointerdown.stop="onXThumbPointer" :style="{ width: thumb.w + 'px', transform: 'translateX(' + thumb.l + 'px)' }"></div>
            </div>
          </div>
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
import { onMounted, onBeforeUnmount, ref, watch, computed, provide, nextTick, reactive } from 'vue'
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

// 在主页面打开浮动控制台（独立页回到父窗口）
function openInOpener() {
  try {
    if (!window.opener) throw new Error('no opener')
    const same = (() => { try { return window.opener.location.origin === window.location.origin } catch { return false } })()
    if (!same) throw new Error('different origin')
    const payload: any = { connId: state.selectedConnId, database: state.selectedDb || '', sql: state.sql || '' }
    // 将 SQL 限制长度，避免过长消息（可选）
    try { if (payload.sql && payload.sql.length > 50000) payload.sql = payload.sql.slice(0, 50000) } catch {}
    window.opener.postMessage({ type: 'open-sql-modal', payload }, window.location.origin)
    try { window.opener.focus() } catch {}
  } catch (e) {
    alert('未检测到主页面或跨域，无法自动打开。请手动切回主页面。')
  }
}
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
    // 不使用 noopener，保证 window.opener 可用于回到主页面打开浮动层（同源）
    window.open(url, '_blank')
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


// 切换连接：重置选择并刷新数据库与菜单树
async function onConnChange(ev: Event) {
  try {
    const val = (ev.target as HTMLSelectElement).value
    const id = /^\d+$/.test(val) ? Number(val) : val
    // 更新选中连接
    try { (state as any).selectedConnId = id } catch {}
    // 清空与上个连接相关的状态
    try { state.selectedDbs = [] } catch {}
    try { (state as any).expandedDb = {} } catch {}
    try { state.filter = '' } catch {}
    try { state.tables = {} as any } catch {}
    try { state.selectedDb = '' as any } catch {}
    try { state.dbDropdownOpen = false } catch {}
    try { state.databases = [] as any } catch {}
    // 重新加载数据库列表并兜底初始化
    // 重新加载默认库的表（如已选择库）
    try { if (state.selectedDb) await loadTables(state.selectedDb) } catch {}
    try { await initConsole(id as any) } catch {}
  } catch {}
}


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
  // 初始化编辑器高度：若未设置则给一个默认值（允许后续拖到 0）
  try {
    const h = Number(state.editorHeight || 0)
    if (!Number.isFinite(h)) (state as any).editorHeight = 150
  } catch {}
  // 文档点击：点击外部关闭 DB 下拉
  document.addEventListener('mousedown', onDocClickCloseDb, true)
  // 初始渲染后：计算列宽并做一次横向联动
  await nextTick()
  try { computeColWidths() } catch {}
  await nextTick(); onXScroll(); adjustHeaderGutter(); updateThumbFromBody()
  attachBodyScrollListener()
  startXSync()
  try { window.addEventListener('resize', adjustHeaderGutter, { passive: true }) } catch {}
  // 强制关闭页面级横向滚动条
  try { document.documentElement.style.overflowX = 'hidden'; document.body.style.overflowX = 'hidden' } catch {}
})

watch(() => state.page, async (p) => {
  pageInput.value = (p as unknown as number) || 1
  // 翻页后重置滚动位置，避免保留上页的 scrollLeft 导致错位或“看不到数据”
  await nextTick()
  try {
    const xs = tqScrollXRef.value as HTMLElement | null
    const body = getBodyScrollEl()
    const head = getHeadScrollEl()
    if (xs) xs.scrollLeft = 0
    if (body) body.scrollLeft = 0
    if (head) head.scrollLeft = 0
  } catch {}
  // 翻页后计算列宽
  await nextTick(); try { computeColWidths() } catch {}
  await nextTick(); onXScroll(); adjustHeaderGutter(); updateThumbFromBody()
  // 最终以实际 body.scrollWidth 回填 spacer 宽度，避免第二页渲染时横向宿主与底部条不同步
  await nextTick();
  try {
    const body = document.querySelector('.page .tq-table-fixed .tq-body') as HTMLElement | null
    if (body && body.scrollWidth) (state as any).bodyTableWidth = body.scrollWidth
    // 清理任何视觉兜底位移
    try {
      const inner = document.querySelector('.page .tq-table-fixed .tq-body-inner') as HTMLElement | null
      const headInner = document.querySelector('.page .tq-table-fixed .tq-scroll-x .tq-head-inner') as HTMLElement | null
      if (inner) inner.style.transform = ''
      if (headInner) headInner.style.transform = ''
    } catch {}
  } catch {}
  onXScroll(); updateThumbFromBody(); attachBodyScrollListener()
  startXSync()
})

// 结果变化后，计算列宽与容器宽度
watch(() => state.result, async () => {
  await nextTick()
  try { computeColWidths() } catch {}
  // 结果变更后，基于底部横条当前位置做一次横向同步
  await nextTick(); onXScroll(); adjustHeaderGutter(); updateThumbFromBody(); attachBodyScrollListener()
  startXSync()
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
// 自定义底部横条：轨道与拇指
const tqXTrackRef = ref<HTMLElement | null>(null)
const tqXThumbRef = ref<HTMLElement | null>(null)
const thumb = reactive({ w: 24, l: 0 })
let __thumbDragging = false
let __thumbStartX = 0
let __thumbStartSL = 0
let __bodyScrollEl: HTMLElement | null = null

// 计算表体尺寸与当前位置
function getBodyDims() {
  const body = getBodyScrollEl()
  if (!body) return { sw: 0, cw: 0, sl: 0 }
  return { sw: body.scrollWidth || 0, cw: body.clientWidth || 0, sl: body.scrollLeft || 0 }
}
// 根据表体当前状态，计算拇指宽度与位置
function updateThumbMetrics() {
  try {
    const track = tqXTrackRef.value as HTMLElement | null
    const { sw, cw, sl } = getBodyDims()
    if (!track || sw <= 0 || cw <= 0) { thumb.w = 24; thumb.l = 0; return }
    const ratio = Math.min(1, cw / sw)
    const trackW = track.clientWidth || 1
    const minThumb = 24
    const tw = Math.max(minThumb, Math.floor(trackW * ratio))
    const maxScroll = Math.max(0, sw - cw)
    const maxThumbLeft = Math.max(0, trackW - tw)
    const tl = maxScroll > 0 ? Math.min(maxThumbLeft, Math.floor((sl / maxScroll) * maxThumbLeft)) : 0
    thumb.w = tw
    thumb.l = tl
  } catch {}
}
function updateThumbFromBody() { updateThumbMetrics() }
// 将拇指位置映射为表体 scrollLeft
function setBodyScrollLeftByThumb(px: number) {
  try {
    const track = tqXTrackRef.value as HTMLElement | null
    const body = getBodyScrollEl()
    if (!track || !body) return
    const trackW = track.clientWidth || 1
    const maxThumbLeft = Math.max(0, trackW - (thumb.w || 0))
    const clamped = Math.min(maxThumbLeft, Math.max(0, px))
    const maxScroll = Math.max(0, (body.scrollWidth || 0) - (body.clientWidth || 0))
    const targetSL = maxThumbLeft > 0 ? Math.round((clamped / maxThumbLeft) * maxScroll) : 0
    if (body.scrollLeft !== targetSL) body.scrollLeft = targetSL
    thumb.l = clamped
  } catch {}
}
// 事件：拖拽拇指
function onXThumbPointer(ev: PointerEvent) {
  try {
    const body = getBodyScrollEl()
    if (!body) return
    __thumbDragging = true
    __thumbStartX = ev.clientX
    __thumbStartSL = body.scrollLeft || 0
    const el = ev.currentTarget as HTMLElement
    el.setPointerCapture?.(ev.pointerId)
    window.addEventListener('pointermove', onXThumbMove, { passive: false })
    window.addEventListener('pointerup', onXThumbUp, { passive: true, once: true })
    ev.preventDefault()
  } catch {}
}
function onXThumbMove(ev: PointerEvent) {
  if (!__thumbDragging) return
  try {
    const track = tqXTrackRef.value as HTMLElement | null
    const body = getBodyScrollEl()
    if (!track || !body) return
    const dx = ev.clientX - __thumbStartX
    const trackW = track.clientWidth || 1
    const maxThumbLeft = Math.max(0, trackW - (thumb.w || 0))
    const maxScroll = Math.max(0, body.scrollWidth - body.clientWidth)
    const startThumb = maxScroll > 0 ? (__thumbStartSL / maxScroll) * maxThumbLeft : 0
    setBodyScrollLeftByThumb(startThumb + dx)
    ev.preventDefault()
  } catch {}
}
function onXThumbUp() {
  __thumbDragging = false
  try { window.removeEventListener('pointermove', onXThumbMove as any) } catch {}
}
// 事件：点击轨道定位
function onXTrackPointer(ev: PointerEvent) {
  try {
    const track = tqXTrackRef.value as HTMLElement | null
    if (!track) return
    const rect = track.getBoundingClientRect()
    const x = ev.clientX - rect.left - (thumb.w || 0) / 2
    setBodyScrollLeftByThumb(x)
  } catch {}
}

// —— rAF 同步兜底：当原生滚动事件异常时，持续以底部横条为源同步表体与表头 ——
let __xsync_rid = 0
let __last_xs_sl = -1
let __x_mismatch_frames = 0
function xSyncLoop() {
  try {
    // 以 .tq-body 为唯一横向滚动宿主与“真源”
    const body = getBodyScrollEl()
    if (!body) { __xsync_rid = requestAnimationFrame(xSyncLoop); return }
    const sl = body.scrollLeft || 0
    const head = getHeadScrollEl()
    if (head && head.scrollLeft !== sl) head.scrollLeft = sl
    // 同步底部自定义拇指
    updateThumbFromBody()
    __last_xs_sl = sl
  } catch {}
  __xsync_rid = requestAnimationFrame(xSyncLoop)
}
function startXSync() {
  try { cancelAnimationFrame(__xsync_rid) } catch {}
  __last_xs_sl = -1
  __xsync_rid = requestAnimationFrame(xSyncLoop)
}
function stopXSync() {
  try { cancelAnimationFrame(__xsync_rid) } catch {}
  __xsync_rid = 0
}

function onXWheel(ev: WheelEvent) {
  try {
    const xs = tqScrollXRef.value as HTMLElement | null
    const body = getBodyScrollEl()
    const head = getHeadScrollEl()
    if (!xs || !body) return
    const dx = Math.abs(ev.deltaX) > Math.abs(ev.deltaY) ? ev.deltaX : ev.deltaY
    const max = Math.max(0, body.scrollWidth - body.clientWidth)
    const target = Math.min(max, Math.max(0, (body.scrollLeft || 0) + dx))
    if (body.scrollLeft !== target) body.scrollLeft = target
    if (head && head.scrollLeft !== target) head.scrollLeft = target
    if (xs.scrollLeft !== target) xs.scrollLeft = target
    ev.preventDefault()
    // 同步后立即检查，必要时应用 transform 矫正
    try {
      const tableRoot = document.querySelector('.page .tq-table-fixed') as HTMLElement | null
      const inner = tableRoot?.querySelector('.tq-body-inner') as HTMLElement | null
      const headInner = tableRoot?.querySelector('.tq-scroll-x .tq-head-inner') as HTMLElement | null
      if (Math.abs((body.scrollLeft || 0) - target) > 1) {
        if (inner) inner.style.transform = target ? `translate3d(${-target}px, 0, 0)` : ''
        if (headInner) headInner.style.transform = target ? `translate3d(${-target}px, 0, 0)` : ''
      } else {
        if (inner && inner.style.transform) inner.style.transform = ''
        if (headInner && headInner.style.transform) headInner.style.transform = ''
      }
    } catch {}
  } catch {}
}

// 激活标签：走组合式方法，并在切换后同步编辑器内容
function activateQueryTab(id: string) {
  try { setActiveTab(id) } catch { state.activeQueryTabId = id }
  nextTick(() => { try { ensureSqlEditor(tqCodeRef.value as any) } catch {} })
}

// 展示后端已分页的数据：后端已按 page/pageSize 返回本页 rows，这里不再二次切片
function getDisplayedRows() {
  try {
    if (!(state.result && (state.result as any).rows)) return []
    return (state.result as any).rows || []
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
    // 自定义底部条：同步拇指位置
    updateThumbFromBody()
  } catch {}
}

function attachBodyScrollListener() {
  try {
    const cur = getBodyScrollEl()
    if (__bodyScrollEl === cur) return
    if (__bodyScrollEl) {
      try { __bodyScrollEl.removeEventListener('scroll', onBodyScroll as any) } catch {}
    }
    __bodyScrollEl = cur
    if (__bodyScrollEl) {
      __bodyScrollEl.addEventListener('scroll', onBodyScroll as any, { passive: true })
    }
  } catch {}
}

function onXScroll() {
  // 自定义横条不依赖原生 scroll，不做任何处理
}

// 同步所有候选数据体容器的 scrollLeft，避免只动表头
function scrollBodies(sl: number) {
  try {
    const tableRoot = (document.querySelector('.page .tq-table-fixed') as HTMLElement | null)
    const root = (tqBodyRef.value as HTMLElement | null) || tableRoot || document.body
    if (!root) return
    // 1) 先覆盖已知候选选择器
    const sels = ['.tq-body', '.tq-body-inner', '.tq-table-fixed .tq-body']
    for (const sel of sels) {
      const list = Array.from((tableRoot || root).querySelectorAll(sel)) as HTMLElement[]
      for (const el of list) { if (el.scrollLeft !== sl) el.scrollLeft = sl }
    }
    // 2) 再遍历所有后代，凡是可横向滚动的节点一并对齐（兜底覆盖重渲染后宿主变化）
    const all = Array.from((tableRoot || root).querySelectorAll('*')) as HTMLElement[]
    for (const el of all) {
      if (!el) continue
      const sw = el.scrollWidth || 0
      const cw = el.clientWidth || 0
      if (sw > cw && el.scrollLeft !== sl) el.scrollLeft = sl
    }
  } catch {}
}

function getBodyScrollEl(): HTMLElement | null {
  // 正确的横/纵滚动宿主是 .tq-body；优先返回 tqBodyRef，其次在其内部探测
  const bodyRef = tqBodyRef.value as HTMLElement | null
  if (bodyRef && (bodyRef.scrollWidth > bodyRef.clientWidth || bodyRef.scrollHeight > bodyRef.clientHeight)) return bodyRef
  // 兜底：在结果区内探测最大可横向滚动的容器作为 body（但应优先 .tq-body）
  const direct = document.querySelector('.page .tq-table-fixed .tq-body') as HTMLElement | null
  if (direct) return direct
  const root = bodyRef || (tqBodyTableRef.value as HTMLElement | null)
  if (!root) return bodyRef || null
  const candidates = [root, ...Array.from(root.querySelectorAll('*')) as HTMLElement[]]
  let best: HTMLElement | null = null
  let bestOverflow = 0
  for (const c of candidates) {
    const csw = c.scrollWidth || 0
    const ccw = c.clientWidth || 0
    const overflow = csw - ccw
    if (overflow > bestOverflow) { bestOverflow = overflow; best = c }
  }
  return best || bodyRef
}

function getHeadScrollEl(): HTMLElement | null {
  // 优先 ref；否则在结果区中查找最可能的表头滚动容器（较矮且可横向滚动）
  const el = tqHeadTableRef.value as HTMLElement | null
  if (el && el.scrollWidth > el.clientWidth) return el
  const root = tqBodyRef.value as HTMLElement | null
  if (!root) return null
  // 直接查找 sticky 头部容器
  const hx = document.querySelector('.page .tq-table-fixed .tq-scroll-x') as HTMLElement | null
  if (hx) return hx
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

function syncHorizontal() {
  try {
    const xs = tqScrollXRef.value as HTMLElement | null
    const body = getBodyScrollEl()
    const head = getHeadScrollEl()
    const sl = xs?.scrollLeft || 0
    if (body && body.scrollLeft !== sl) body.scrollLeft = sl
    if (head && head.scrollLeft !== sl) head.scrollLeft = sl
    scrollBodies(sl)
  } catch {}
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
function adjustHeaderGutter() {
  try {
    const root = document.querySelector('.page .tq-table-fixed') as HTMLElement | null
    const body = document.querySelector('.page .tq-table-fixed .tq-body') as HTMLElement | null
    const head = document.querySelector('.page .tq-table-fixed .tq-scroll-x') as HTMLElement | null
    if (!root || !body || !head) return
    // 计算表体竖向滚动条宽度（有滚动条则 >0）
    const vbar = Math.max(0, (body.offsetWidth || 0) - (body.clientWidth || 0))
    head.style.setProperty('--tq-vbar', vbar + 'px')
    // 基于 DPR 的子像素补偿：高 DPI 或缩放下适当放大补偿至 2px
    const dpr = (window.devicePixelRatio || 1)
    const comp = dpr >= 1.25 ? 3 : (dpr > 1.1 ? 2 : 1)
    head.style.setProperty('--tq-comp', comp + 'px')
    // 临时右移表头 9px 进行对齐测试
    head.style.setProperty('--tq-head-shift', '9px')
    // 同步头部可滚区域的 scrollLeft（防止初次渲染出现轻微偏差）
    const xs = tqScrollXRef.value as HTMLElement | null
    const sl = xs?.scrollLeft || 0
    const headEl = getHeadScrollEl()
    if (headEl && headEl.scrollLeft !== sl) headEl.scrollLeft = sl
  } catch {}
}
function startResize(ev?: MouseEvent) {
  try {
    const container = rightRef.value as HTMLElement | null
    if (!container) return
    const startY = (ev?.clientY ?? 0)
    const initH = Number(state.editorHeight || 220)
    const minH = 0
    // 与独立页面统一：结果区最小高度 140，避免分隔条侵入编辑器区域
    const minResult = 140
    const maxH = Math.max(minH + 80, (container.clientHeight || 600) - minResult)
    const onMove = (e: MouseEvent) => {
      try {
        const dy = e.clientY - startY
        let h = initH + dy
        if (!Number.isFinite(h)) h = initH
        h = Math.max(minH, Math.min(maxH, Math.floor(h)))
        ;(state as any).editorHeight = h
        try {
          const wrap = document.querySelector('.tq-editor-wrap') as HTMLElement | null
          const editor = document.querySelector('.tq-editor') as HTMLElement | null
          if (wrap) wrap.style.height = Math.max(0, h) + 'px'
          if (editor) editor.style.height = Math.max(0, h) + 'px'
        } catch {}
      } catch {}
    }
    const onUp = () => {
      try { window.removeEventListener('mousemove', onMove) } catch {}
      try { window.removeEventListener('mouseup', onUp) } catch {}
      try { document.body.style.userSelect = '' } catch {}
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp, { once: true })
    try { document.body.style.userSelect = 'none' } catch {}
  } catch {}
}
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
  stopXSync()
  try { window.removeEventListener('resize', adjustHeaderGutter as any) } catch {}
  try { document.documentElement.style.overflowX = ''; document.body.style.overflowX = '' } catch {}
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
.dv-sql-console { height: 100vh; display: flex; flex-direction: column; overflow-anchor: none; overflow-x: hidden; }
.tq-title { flex: 0 0 auto; padding: 10px 12px; border-bottom: 1px solid #e5e7eb; background: #fff; display:flex; align-items:center; gap:8px; height: 60px; box-sizing: border-box; }
.tq-title .t { font-size: 18px; line-height: 22px; font-weight: 700; color: #1d4ed8; letter-spacing: .2px; }
.tq-title .i { font-size: 14px; line-height: 20px; color: #6b7280; }
/* 统一标题栏高度：浮动与独立窗口均为 60px */
.tq-title { height: 60px; }
.card.section-block.tq-toolbar { flex: 0 0 auto; }
.card.section-block.tq-toolbar { height: 48px; box-sizing: border-box; }
.tq-toolbar-row { height: 100%; align-items: center; }
/* 顶部与内容之间的留白，贴近工单查询 */
.tq-main { margin-top: 8px; }
.tq-main { overflow-x: hidden; }
.tq-main { flex: 1 1 auto; min-height: 0; height: auto; display: grid; grid-template-columns: repeat(12, 1fr); grid-template-rows: 1fr; gap: 0; padding: 0; background: #f8fafc; position: relative; contain: layout paint; }
.tq-main.left-collapsed { grid-template-columns: 0 repeat(11, 1fr); }
/* 左树作为滚动宿主，父容器不滚动 */
.tq-left { grid-column: 1; background: #f8fafc; border-right: 1px solid #e5e7eb; height: 100%; display: flex; flex-direction: column; overflow: hidden; min-height: 0; position: relative; z-index: 50; pointer-events: auto; box-sizing: border-box; contain: layout paint; }
.tq-main.left-collapsed .tq-left { display: none !important; border-right: none !important; }
.tq-main.left-collapsed .tq-right { grid-column: 1 / -1 !important; }
.tq-tree { padding: 8px; flex: 1 1 auto; min-height: 0; overflow: auto; scrollbar-width: thin; font-size:14px; scrollbar-gutter: stable both-edges; overflow-anchor: none; }
.tq-tree { scrollbar-color: #94a3b8 transparent; }
.tq-tree::-webkit-scrollbar { width: 10px; height: 10px; }
.tq-tree::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 6px; }
.tq-tree::-webkit-scrollbar-thumb:hover { background: #64748b; }
.tq-tree::-webkit-scrollbar-track { background: transparent; }
.tq-tree-db-name { display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 4px 10px; border-radius: 6px; line-height: 28px; color:#0b57d0; font-weight: 400; }
.tq-tree-db-name:hover { background: #eef2ff; }
.tq-tree-tables { list-style: none; padding-left: 16px; margin: 4px 0 8px; font-size:14px; }
.tq-tree-tables li { line-height: 28px; padding: 2px 10px; border-radius: 4px; color:#334155; }
.tq-tree-tables li:hover { background:#f2f6ff; }
.tq-tree-db-name .arrow { display: inline-block; width: 10px; transform: rotate(90deg); transition: transform .15s; color:#64748b; font-size:12px; }
.tq-right { grid-column: 2; display: flex; flex-direction: column; height: 100%; min-height: 0; min-width: 0; z-index: 10; }
.tq-right { contain: layout paint; }
.tq-editor-wrap { background: #fff; border-bottom: none; display: flex; align-items: stretch; justify-content: flex-start; color: #64748b; width: 100%; }
.tq-editor-wrap > * { width: 100%; max-width: none; }
.tq-editor-wrap :deep(.tq-sql),
.tq-editor-wrap :deep(.cm-editor) { width: 100% !important; }
.tq-editor-placeholder { padding: 24px; font-size: 14px; }
.tq-editor-placeholder { padding: 24px; font-size: 14px; }
.tq-result { flex: 1; display: flex; flex-direction: column; min-height: 0; border: 1px solid #e5e7eb; border-radius: 8px; background: #fff; position: relative; z-index: 1; overflow: hidden; }
.tq-result-body { position: relative; flex: 1 1 auto; min-height: 0; overflow: hidden; padding: 12px 12px 16px; scrollbar-gutter: stable both-edges; overflow-anchor: none; z-index: 2; background: #fff; }
.page .tq-result-body { padding-left: 0; padding-right: 0; scrollbar-gutter: auto; }
/* 独立窗口：去掉结果表格区域的任何左侧内外边距，让表格贴齐左边 */
.page .tq-result-body .tq-table-fixed,
.page .tq-result-body .tq-scroll-x,
.page .tq-result-body .tq-body,
.page .tq-result-body .tq-body-inner { margin-left: 0 !important; padding-left: 0 !important; }
/* 浮动窗口：为占位文案与下方横线留足距离，避免视觉压线 */
.tq-result-body { position: relative; flex: 1 1 auto; min-height: 0; overflow: hidden; padding: 12px 12px 16px; scrollbar-gutter: stable both-edges; overflow-anchor: none; z-index: 2; background: #fff; }
.tq-result-scroll { width: 100%; height: 100%; overflow-y: auto; overflow-x: hidden; scrollbar-gutter: stable both-edges; overflow-anchor: none; }
/* 独立页：外层不承担读纵向滚动，由表体承担（起点=第1行） */
.page .tq-result-body { display: flex; flex-direction: column; min-height: 0; }
.page .tq-result-scroll { position: relative; flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; overflow-x: hidden !important; overflow-y: hidden !important; scrollbar-gutter: auto; }
/* 保持表体仅负责横向滚动（底部外置横条联动） */
.page :deep(.tq-body) { overflow-x: hidden !important; }
.page :deep(.result-table) .tq-body { overflow-x: hidden !important; }
.tq-x-scroll { flex: 0 0 auto; height: 14px; overflow-x: auto; overflow-y: hidden; border-top: 1px solid #e5e7eb; background: #fff; width: 100%; max-width: 100%; }
.modal .tq-x-scroll { border-top: none; }
.page .tq-x-scroll { display: block !important; height: 10px; }
.page :deep(.result-table) .tq-body { margin-bottom: 6px; }
/* 结果表容器使用纵向 Flex，确保表头占自然高度，表体可伸展且可滚动 */
/* 结果表容器使用纵向 Flex，表体占剩余空间 */
/* 与浮动窗一致：结果表容器纵向布局，表体承担纵向滚动（注意真实类名为 .tq-table-fixed/.tq-body） */
.page :deep(.tq-table-fixed) { display: flex; flex-direction: column; min-height: 0; }
.page :deep(.tq-body) { flex: 1 1 auto; min-height: 0; overflow-y: auto !important; overflow-x: hidden !important; }
/* 统一表体纵向滚动条为 8px（应用于 .tq-body） */
.page :deep(.tq-body) { scrollbar-width: thin; }
.page :deep(.tq-body)::-webkit-scrollbar { width: 10px; height: 10px; }
.page :deep(.tq-body)::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 6px; }
.page :deep(.tq-body)::-webkit-scrollbar-thumb:hover { background: #64748b; }
.page :deep(.tq-body)::-webkit-scrollbar-track { background: transparent; }
/* 仅隐藏表体的横向滚动条外观（保留横向滚动用于与底部条联动） */
.page :deep(.tq-body)::-webkit-scrollbar:horizontal { height: 0 !important; }
/* —— 仅保留底部浅色横向滚动条（page 模式）—— */
/* 允许内部 body 横向滚动，但隐藏其横向滚动条的可见性，从而由底部浅色条驱动同步 */
.page :deep(.result-table) .tq-body { overflow-x: hidden !important; }
/* scrollbar-width: none; -ms-overflow-style: none; */
.page :deep(.tq-body-inner) { overflow-x: visible !important; }
/* 不再通配隐藏所有滚动条，避免影响纵向；仅在下方针对横向隐藏外观 */
/* 兜底再隐藏轨道与拇指（横向） */
.page :deep(.tq-body)::-webkit-scrollbar:horizontal { height: 0 !important; background: transparent !important; }
.page :deep(.tq-body)::-webkit-scrollbar-thumb:horizontal { background: transparent !important; }
.page :deep(.result-table) .tq-head-inner { order: unset; position: static; top: auto; z-index: auto; }
.page :deep(.result-table) .tq-scroll-x { display: none !important; position: static; top: auto; z-index: auto; height: 0; }
/* 浮动窗口（modal）同样隐藏表头横向滚动条，避免双横条 */
.modal :deep(.result-table) .tq-scroll-x { display: none !important; position: static; top: auto; z-index: auto; height: 0; }
.tq-x-scroll .spacer { height: 1px; }
.tq-pagination { flex: 0 0 auto; display: flex; align-items: center; gap: 12px; padding: 8px 12px; border-top: 1px solid #e5e7eb; background: #fff; color:#374151; }
.tq-pagination .muted { color: #64748b; }
/* 左右翻页按钮：与工单查询一致的圆角、尺寸与配色 */
.tq-pagination .icon-btn { width: 28px; height: 28px; border-radius: 10px; border-color: #e5e7eb; background: #fff; color:#0b57d0; }
.tq-pagination .icon-btn:hover { background:#f8fafc; }
/* 自定义底部横条：样式对齐左侧菜单滚动条（细拇指、圆角、浅色） */
 .tq-x-scroll { flex: 0 0 auto; height: 6px; overflow: hidden; border-top: 1px solid #e5e7eb; background: #fff; position: relative; }
/* 轨道与菜单滚动条风格一致：弱化轨道背景 */
.tq-x-scroll .x-track { position: relative; width: 100%; height: 6px; background: transparent; border-radius: 999px; cursor: pointer; }
/* 拇指颜色与菜单滚动条保持一致 */
.tq-x-scroll .x-thumb { position: absolute; left: 0; top: 0; height: 6px; background: #94a3b8; border-radius: 999px; will-change: transform; }
.tq-x-scroll .x-thumb:hover { background: #64748b; }

/* （回退）不在 modal 统一纵向滚动条，避免影响独立页表现 */
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

/* 固定标签栏首帧高度与行高，贴合浮动窗口，避免初始装载跳动 */
.tq-tabs-wrap { height: 36px; display: flex; align-items: center; padding: 0 8px; background: #fff; border-bottom: 1px solid #e5e7eb; box-sizing: border-box; }

/* toolbar spacing utilities per spec */
.tq-ml10 { margin: 0; margin-left: 10px; }
/* —— 最终覆盖（独立页）：仅表体纵向滚动，外层不纵滚，滚动起点=第1行 —— */
.page .tq-result-scroll { overflow-y: hidden !important; overflow-x: hidden !important; display: flex; flex-direction: column; }
.page :deep(.tq-table-fixed) { display: flex !important; flex-direction: column !important; flex: 1 1 auto !important; min-height: 0 !important; }
.page :deep(.tq-table-fixed) .tq-body { flex: 1 1 auto !important; height: 100% !important; min-height: 0 !important; overflow-y: auto !important; overflow-x: hidden !important; scrollbar-gutter: stable both-edges; }
/* 仅隐藏表体横向滚动条外观，不影响纵向 */
.page :deep(.tq-body)::-webkit-scrollbar:horizontal { height: 0 !important; background: transparent !important; }
.page :deep(.tq-body)::-webkit-scrollbar-thumb:horizontal { background: transparent !important; }
.page :deep(.tq-scroll-x) { padding-right: calc(var(--tq-vbar, 0px) + 5px); box-sizing: content-box; }
.page :deep(.tq-scroll-x .tq-head-inner) { margin-left: var(--tq-head-shift, 0px); }
.tq-ml20 { margin: 0; margin-left: 20px; }
.tq-mr10 { margin: 0; margin-right: 10px; }

/* 全局关闭页面级横向滚动条，避免 window 抢占横向交互 */
:global(html), :global(body) { overflow-x: hidden; }

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
.tq-result-body > .muted { display: inline-block; margin-top: 10px; }
/* 浮动窗口：将占位文案固定在底部上方 24px，彻底避免与边线/横条相交 */
/* 统一占位样式：与独立页一致（不绝对定位） */
.tq-result-body > .muted { display: inline-block; margin-top: 10px; }

/* 执行中提示条（不覆盖内容，居中展示） */
.tq-executing { position: static; display: inline-flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 8px; background: #f8fafc; color: #475569; font-size: 13px; line-height: 20px; box-shadow: inset 0 0 0 1px #e5e7eb; margin: 12px auto; }
.tq-executing .spinner { width: 14px; height: 14px; border: 2px solid #cbd5e1; border-top-color: #60a5fa; border-radius: 50%; animation: tqspin 1s linear infinite; display:inline-block; }
@keyframes tqspin { from { transform: rotate(0); } to { transform: rotate(360deg); } }

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
.tq-conn-select { color:#0b57d0; font-size:14px; line-height:22px; height:32px; padding:4px 8px; border:1px solid #c7d2fe; border-radius:6px; background:#fff; box-sizing:border-box; width: 100%; outline: none; }
.tq-conn-select:focus,
.tq-conn-select:active,
.tq-conn-select:focus-visible { outline: none; border-color:#3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,.12); border-width:1px; }
.icon-label:focus-within { outline: none; }
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
.tq-vsplit { position: relative; height: 12px; cursor: row-resize; background: transparent; }
.tq-vsplit::before { content: ""; position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 36px; height: 4px; border-radius: 999px; background: #d1d5db; box-shadow: 0 1px 0 rgba(0,0,0,.04); }
.tq-vsplit:hover { background: transparent; }
.tq-vsplit:hover::before { background: #c7d2fe; }
.tq-vsplit:active { background: transparent; }
.tq-vsplit:active::before { background: #93c5fd; }
/* 独立窗口（page）与浮动窗口一致：移除分隔条把手的阴影线 */
.page .tq-vsplit::before { box-shadow: none; }
/* 独立窗口：分隔条把手更细一点 */
.page .tq-vsplit::before { height: 2px; }
/* 独立窗口：查询结果下方的提示文字更小一号 */
.page .tq-result-body > .muted { font-size: 12px; }
/* 分隔条样式与独立页一致（无额外偏移） */
/* —— 仅内嵌窗口（modal）：统一纵向滚动条为 6px，与菜单一致 —— */
.modal :deep(.cm-body)::-webkit-scrollbar,
.modal :deep(.tq-tree)::-webkit-scrollbar,
.modal :deep(.tq-body)::-webkit-scrollbar { width: 10px; height: 10px; }
.modal :deep(.tq-body)::-webkit-scrollbar:horizontal { height: 0 !important; background: transparent !important; }
.modal :deep(.cm-body)::-webkit-scrollbar-thumb,
.modal :deep(.tq-tree)::-webkit-scrollbar-thumb,
.modal :deep(.tq-body)::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 6px; }
.modal :deep(.cm-body)::-webkit-scrollbar-thumb:hover,
.modal :deep(.tq-tree)::-webkit-scrollbar-thumb:hover,
.modal :deep(.tq-body)::-webkit-scrollbar-thumb:hover { background: #64748b; }
/* 仅作用纵向；横向条保持：底部 .tq-x-scroll 自定义 6px，不动 */

/* —— 针对内嵌控制台面板容器（更精确作用域）：.dv-modal-panel.ticket-query —— */
.dv-modal-panel.ticket-query :deep(.cm-body)::-webkit-scrollbar,
.dv-modal-panel.ticket-query :deep(.tq-tree)::-webkit-scrollbar,
.dv-modal-panel.ticket-query :deep(.tq-body)::-webkit-scrollbar { width: 10px; height: 10px; }
.dv-modal-panel.ticket-query :deep(.cm-body)::-webkit-scrollbar-thumb,
.dv-modal-panel.ticket-query :deep(.tq-tree)::-webkit-scrollbar-thumb,
.dv-modal-panel.ticket-query :deep(.tq-body)::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 6px; }
.dv-modal-panel.ticket-query :deep(.cm-body)::-webkit-scrollbar-thumb:hover,
.dv-modal-panel.ticket-query :deep(.tq-tree)::-webkit-scrollbar-thumb:hover,
.dv-modal-panel.ticket-query :deep(.tq-body)::-webkit-scrollbar-thumb:hover { background: #64748b; }
</style>
 
