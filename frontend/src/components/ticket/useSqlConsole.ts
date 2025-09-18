/*
  Composable: useSqlConsole
  目的：将 App.vue 中与“工单查询-SQL控制台”相关的状态与方法逐步抽取到此处，
  以便被浮层组件与独立窗口页面复用。
  当前为第一步：创建可用的骨架与类型定义，不改变现有逻辑调用链。
*/

import { ref, reactive, computed, nextTick, onMounted, onBeforeUnmount, type Ref, type ComputedRef } from 'vue'
// 统一使用现有 api 实例
// 相对路径以使用此组合式在同级组件中被引用
// 注意：父项目已有 axios 封装 src/api.ts
// 这里直接引用供请求使用
// @ts-ignore
import api from '../../api'

export type TResultTable = {
  type: 'table'
  columns: string[]
  rows: Array<Record<string, any>>
}

export type TResultText = {
  type: 'text'
  text: string
}

export type TResult = TResultTable | TResultText | null

export interface SqlConsoleState {
  // 连接与数据库
  conns: any[]
  selectedConnId: number | string | ''
  databases: string[]
  selectedDb: string
  selectedDbs: string[]
  tables: Record<string, string[]>
  tablesLoading: Record<string, boolean>
  expandedDb?: Record<string, boolean>

  // 查询/结果/分页
  sql: string
  result: TResult
  running: boolean
  page: number
  pageSize: number
  totalRows: number
  respectInnerLimit: boolean

  // UI
  editorHeight: number
  freezeCount: number
  freezeLefts?: number[]
  tableColWidths?: number[]
  bodyTableWidth?: number
  dbDropdownOpen: boolean
  forceTreeFilter: boolean
  tableFilters: Record<string, string>
  leftCollapsed: boolean
  filter: string
  // tabs
  qTabs: Array<{ id: string, title: string, ui?: any, sql?: string, result?: any, running?: boolean, page?: number, pageSize?: number, respectInnerLimit?: boolean }>
  activeQueryTabId: string
  // sort
  sortKey?: string
  sortDir?: '' | 'asc' | 'desc'
  // input
  pageInput?: number
}

export interface UseSqlConsole {
  // state
  state: SqlConsoleState

  // computed helpers
  filteredDatabases: ComputedRef<string[]>
  filteredTables: (db: string) => string[]

  // lifecycle
  initConsole: (connId: number | string) => Promise<void>

  // editor
  ensureSqlEditor: (host?: HTMLElement | null) => Promise<void>
  focusSqlEditor: () => void

  // actions
  executeSQL: () => Promise<void>
  stopExecution: () => void
  viewPlan: () => Promise<void>
  beautifySQL: () => void
  loadTables: (db: string) => Promise<void>
  appendTableToSQL: (db: string, tbl: string) => Promise<void>

  // ui helpers
  toggleDbDropdown: () => void
  onDbToggle: (db: string, checked: boolean) => void
  clearDbSelection: () => void
  toggleLeftCollapsed: () => void

  // pagination
  totalPages: ComputedRef<number>
  goToPage: (p: number) => Promise<void>

  // export
  exportCSV: () => void
  exportExcel: () => void

  // tabs
  newQueryTab: () => void
  closeQueryTab: (id: string) => void
  setActiveTab: (id: string) => void
}

// 先提供一个最小可用骨架，后续逐步把 App.vue 里的具体实现迁移进来。
export function useSqlConsole(): UseSqlConsole {
  // --- state ---
  const state: SqlConsoleState = reactive({
    conns: [],
    selectedConnId: '',
    databases: [],
    selectedDb: '',
    selectedDbs: [],
    tables: {},
    tablesLoading: {},
    expandedDb: {},

    sql: '',
    result: null,
    running: false,
    page: 1,
    pageSize: 50,
    totalRows: 0,
    respectInnerLimit: false,

    editorHeight: 162,
    freezeCount: 0,
    freezeLefts: [],
    tableColWidths: [],
    bodyTableWidth: 0,
    dbDropdownOpen: false,
    forceTreeFilter: false,
    tableFilters: {},
    leftCollapsed: false,
    filter: '',
    qTabs: [],
    activeQueryTabId: '',
    sortKey: '',
    sortDir: '',
    pageInput: 1,
  })

  // ---- tabs helpers ----
  const activeTab = computed(() => {
    const id = state.activeQueryTabId
    const arr = state.qTabs
    return arr.find(t => t.id === id) || null
  })

  function nextTabTitle(): string {
    const base = 'SQL '
    let i = 1
    const titles = new Set((state.qTabs || []).map(t => t.title))
    while (titles.has(base + i)) i++
    return base + i
  }

  const filteredDatabases: ComputedRef<string[]> = computed(() => {
    const arr = Array.isArray(state.databases) ? state.databases : []
    const kw = (state.filter || '').toLowerCase().trim()
    if (!kw) return arr
    return arr.filter(d => String(d).toLowerCase().includes(kw))
  })

  function _filterTables(arr: string[], kw: string): string[] {
    if (!kw) return arr
    const f = kw.toLowerCase().trim()
    return arr.filter(x => String(x).toLowerCase().includes(f))
  }

  // --- export helpers ---
  function exportCSV() {
    try {
      const res: any = state.result
      if (!(res && res.type === 'table' && Array.isArray(res.rows) && Array.isArray(res.columns))) return
      const cols: string[] = res.columns
      const lines = [] as string[]
      lines.push(cols.map(c => '"' + String(c).replace(/"/g, '""') + '"').join(','))
      for (const row of res.rows) {
        const vals = cols.map(c => '"' + String(row?.[c] ?? '').replace(/"/g, '""') + '"')
        lines.push(vals.join(','))
      }
      const blob = new Blob(["\ufeff" + lines.join("\n")], { type: 'text/csv;charset=utf-8;' })
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = 'query.csv'
      a.click()
      URL.revokeObjectURL(a.href)
    } catch {}
  }

  function exportExcel() {
    // 简化：导出 CSV 即可，被前端 Excel 识别
    exportCSV()
  }

  function filteredTables(db: string): string[] {
    const arr = state.tables[db] || []
    const kw = state.tableFilters?.[db] || ''
    return _filterTables(arr, kw)
  }

  // --- placeholders: 后续将逐步迁移真实实现 ---
  async function initConsole(connId: number | string) {
    state.selectedConnId = typeof connId === 'string' ? (Number(connId) || connId) : connId
    try {
      // 1) 加载连接列表（兜底从 /connections 获取有效连接）
      await loadConns()
      // 2) 加载数据库列表（与现有实现保持一致：/ticket/databases）
      await loadDatabases()
      // 3) 初始化编辑器高度等（不自动展开任何库，不自动选择数据库）
      // 首帧高度兜底：小于 100 则设为 162
      if (!state.editorHeight || state.editorHeight < 100) state.editorHeight = 162
      // 4) 初始化默认标签页
      if (!state.qTabs.length) {
        const id = cryptoRandomId()
        state.qTabs = [{ id, title: nextTabTitle(), sql: '', result: null, running: false, page: 1, pageSize: state.pageSize }]
        state.activeQueryTabId = id
      }
      await ensureSqlEditor()
    } catch (e) {
      // 静默处理，调用方可根据 state 观察
      try { console.error('[useSqlConsole] initConsole error', e) } catch {}
    }
  }

  // 编辑器相关：占位
  async function ensureSqlEditor(host?: HTMLElement | null) {
    await nextTick()
    try {
      // 优先使用明确传入的 host；否则按 SQL 控制台的新类名查找，再兼容旧类名
      let el = host || (document.querySelector('.tq-sql-console') as HTMLElement | null)
      if (!el) el = document.querySelector('.tq-sql') as HTMLElement | null
      if (!el) return
      // 若已被 CodeMirror 接管（cm=on），仅当容器内存在 .cm-editor 时才早退；
      // 若标记存在但 .cm-editor 不在，则清除标记并继续走 contenteditable 兜底。
      if ((el as any)._dvBound || el.dataset.cm === '1' || el.dataset.cmOn === '1') {
        const hasCM = !!el.querySelector('.cm-editor')
        if (hasCM) {
          return
        } else {
          try { delete (el as any)._dvBound; el.removeAttribute('data-cm'); el.removeAttribute('data-cm-on'); } catch {}
        }
      }
      el.setAttribute('contenteditable', 'true')
      el.style.outline = 'none'
      // 确保保留换行与空白
      try { el.style.whiteSpace = 'pre-wrap' } catch {}
      try { (el as any).tabIndex = 0 } catch {}
      el.textContent = (activeTab.value?.sql ?? state.sql) || ''
      const onInput = () => {
        const atTab = activeTab.value
        const valNow = el.textContent || ''
        if (atTab) atTab.sql = valNow
        else state.sql = valNow
      }
      el.removeEventListener('input', onInput as any)
      el.addEventListener('input', onInput as any)
      // 初次绑定和重绑定时，尝试将光标移动到文本末尾并聚焦
      try {
        const range = document.createRange()
        range.selectNodeContents(el)
        range.collapse(false)
        const sel = window.getSelection()
        sel?.removeAllRanges()
        sel?.addRange(range)
        ;(el as HTMLElement).focus()
      } catch {}
      // 再次异步调度一次光标定位，避免后续 DOM 写入导致光标消失
      try {
        requestAnimationFrame(() => {
          setTimeout(() => {
            try {
              const range2 = document.createRange()
              range2.selectNodeContents(el)
              range2.collapse(false)
              const sel2 = window.getSelection()
              sel2?.removeAllRanges()
              sel2?.addRange(range2)
              ;(el as HTMLElement).focus()
            } catch {}
          }, 0)
        })
      } catch {}
      // 标记已由 contenteditable 接管，便于后续逻辑判断
      try { (el as any)._dvBound = true } catch {}
      // 同步一次当前文本到状态
      try {
        const atSync = activeTab.value
        const curVal = el.textContent || ''
        if (atSync) atSync.sql = curVal; else state.sql = curVal
      } catch {}
    } catch {}
  }

  function focusSqlEditor() {
    // 迁移编辑器聚焦逻辑
  }

  // 动作：占位
  async function executeSQL() {
    if (!String((activeTab.value?.sql ?? state.sql) || '').trim()) return
    state.running = true
    const page = Number(state.page) || 1
    const pageSize = Number(state.pageSize) || 50
    try {
      state.result = { type: 'text', text: '执行中...' }
      const at = activeTab.value
      // 优先使用 CodeMirror（cm=on）通过 SqlEditor.vue 同步的最新文本
      const cmMirror = (globalThis as any).__tq_sql_text
      const sqlText = (typeof cmMirror === 'string' && cmMirror.trim())
        ? cmMirror
        : ((at?.sql ?? state.sql) || '')
      const payload = {
        connId: state.selectedConnId,
        database: state.selectedDb || (state.selectedDbs?.[0] || ''),
        sql: sqlText,
        page,
        pageSize,
      }
      const { data } = await api.post('/ticket/execute', payload)

      // 统一规范：优先识别 {data, columns} 或 {rows, columns}
      const rowsA: any[] | undefined = Array.isArray((data as any)?.data) ? (data as any).data : undefined
      const rowsB: any[] | undefined = Array.isArray((data as any)?.rows) ? (data as any).rows : undefined
      const columns: string[] | undefined = Array.isArray((data as any)?.columns) ? (data as any).columns : undefined

      function projectRows(rows: any[], cols?: string[]) {
        if (Array.isArray(cols) && cols.length) {
          // 仅保留并按顺序返回指定列
          return rows.map(r => {
            const o: Record<string, any> = {}
            for (const c of cols) o[c] = r?.[c]
            return o
          })
        }
        return rows
      }

      if ((rowsA || rowsB) && Array.isArray(columns)) {
        const rows = projectRows((rowsA || rowsB) as any[], columns)
        const res = { type: 'table', rows, columns } as any
        state.result = res
        if (at) (at as any).result = res
        const total = Number((data as any).totalRows || (data as any).total || (data as any).count || rows.length || 0)
        state.totalRows = total
        if (at) (at as any).totalRows = total
        // 同步页码/每页
        const newPage = Number((data as any).pageEcho || (data as any).page || page)
        const newPs = Number((data as any).pageSizeEcho || (data as any).pageSize || pageSize)
        state.page = newPage
        state.pageSize = newPs
        if (at) { (at as any).page = newPage; (at as any).pageSize = newPs }
      } else if (Array.isArray(data)) {
        const rows = data
        const cols = rows.length ? Object.keys(rows[0]) : []
        const res = { type: 'table', rows, columns: cols } as any
        state.result = res
        if (at) (at as any).result = res
        state.totalRows = rows.length
        if (at) (at as any).totalRows = rows.length
      } else if (typeof data === 'string') {
        const res = { type: 'text', text: data } as any
        state.result = res
        if (at) (at as any).result = res
      } else if (data && data.message) {
        const res = { type: 'text', text: data.message } as any
        state.result = res
        if (at) (at as any).result = res
      } else {
        const res = { type: 'text', text: '执行完成' } as any
        state.result = res
        if (at) (at as any).result = res
      }
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || '执行失败'
      const res = { type: 'text', text: String(msg) } as any
      state.result = res
      const at = activeTab.value
      if (at) (at as any).result = res
    } finally {
      state.running = false
    }
  }

  function stopExecution() {
    state.running = false
  }

  async function viewPlan() {
    const sqlText = (activeTab.value?.sql ?? state.sql) || ''
    if (!sqlText.trim()) return
    try {
      const payload = {
        connId: state.selectedConnId,
        database: state.selectedDb || (state.selectedDbs?.[0] || ''),
        sql: sqlText,
      }
      const { data } = await api.post('/ticket/plan', payload)
      if (typeof data === 'string') {
        const res = { type: 'text', text: data } as any
        state.result = res
        const at = activeTab.value; if (at) (at as any).result = res
      } else if (data && data.message) {
        const res = { type: 'text', text: data.message } as any
        state.result = res
        const at = activeTab.value; if (at) (at as any).result = res
      } else {
        const res = { type: 'text', text: JSON.stringify(data, null, 2) } as any
        state.result = res
        const at = activeTab.value; if (at) (at as any).result = res
      }
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || '获取执行计划失败'
      const res = { type: 'text', text: String(msg) } as any
      state.result = res
      const at = activeTab.value; if (at) (at as any).result = res
    }
  }

  function beautifySQL() {
    const at = activeTab.value
    const baseSql = (at?.sql ?? state.sql) || ''
    if (!baseSql) return
    let s = baseSql
    s = s.replace(/[\t ]+/g, ' ').replace(/\s*;\s*/g, ';\n').replace(/\n{3,}/g, '\n\n').trim() + '\n'
    if (at) at.sql = s
    state.sql = s
  }

  async function loadTables(db: string) {
    if (!db || !state.selectedConnId) return
    state.tablesLoading[db] = true
    try {
      // 与现有实现兼容的参数名
      const params: any = { connId: state.selectedConnId, db, database: db, schema: db, id: state.selectedConnId }
      const { data } = await api.get('/ticket/tables', { params })
      state.tables[db] = Array.isArray(data) ? data : []
    } catch (e) {
      try { console.error('[useSqlConsole] loadTables error', db, e) } catch {}
      state.tables[db] = state.tables[db] || []
    } finally {
      state.tablesLoading[db] = false
    }
  }

  async function loadDatabases() {
    // 优先尝试 /ticket/databases?connId=xxx
    try {
      const { data } = await api.get('/ticket/databases', { params: { connId: state.selectedConnId, id: state.selectedConnId, connectionId: state.selectedConnId } })
      if (Array.isArray(data) && data.length) {
        state.databases = data
        return
      }
    } catch {}
    // 兜底尝试 /connections/{id}/databases
    try {
      const { data } = await api.get(`/connections/${state.selectedConnId}/databases`)
      state.databases = Array.isArray(data) ? data : []
    } catch (e) {
      state.databases = []
    }
  }

function beautifySQL() {
  const at = activeTab.value
  const baseSql = (at?.sql ?? state.sql) || ''
  if (!baseSql) return
  let s = baseSql
  s = s.replace(/[\t ]+/g, ' ').replace(/\s*;\s*/g, ';\n').replace(/\n{3,}/g, '\n\n').trim() + '\n'
  if (at) at.sql = s
  state.sql = s
}

async function loadTables(db: string) {
  if (!db || !state.selectedConnId) return
  state.tablesLoading[db] = true
  try {
    // 与现有实现兼容的参数名
    const params: any = { connId: state.selectedConnId, db, database: db, schema: db, id: state.selectedConnId }
    const { data } = await api.get('/ticket/tables', { params })
    state.tables[db] = Array.isArray(data) ? data : []
  } catch (e) {
    try { console.error('[useSqlConsole] loadTables error', db, e) } catch {}
    state.tables[db] = state.tables[db] || []
  } finally {
    state.tablesLoading[db] = false
  }
}

async function loadDatabases() {
  // 优先尝试 /ticket/databases?connId=xxx
  try {
    const { data } = await api.get('/ticket/databases', { params: { connId: state.selectedConnId, id: state.selectedConnId, connectionId: state.selectedConnId } })
    if (Array.isArray(data) && data.length) {
      state.databases = data
      return
    }
  } catch {}
  // 兜底尝试 /connections/{id}/databases
  try {
    const { data } = await api.get(`/connections/${state.selectedConnId}/databases`)
    state.databases = Array.isArray(data) ? data : []
  } catch (e) {
    state.databases = []
  }
}

async function loadConns() {
  try {
    const { data } = await api.get('/connections')
    state.conns = Array.isArray(data) ? data : []
  } catch {
    state.conns = state.conns || []
  }
}

async function appendTableToSQL(db: string, tbl: string) {
  const snippet = `-- ${db}.${tbl}\nSELECT * FROM ${db}.${tbl} LIMIT 100;`
  const at = activeTab.value
  const base = (at?.sql ?? state.sql) || ''
  const prefix = base && !/\n$/.test(base) ? '\n' : ''
  const next = base + prefix + snippet
  if (at) at.sql = next
  state.sql = next
  // 片段插入后重新确保编辑器就绪并聚焦，防止光标丢失
  nextTick(() => ensureSqlEditor())
}

function newQueryTab() {
  const id = cryptoRandomId()
  const title = nextTabTitle()
  const tab: any = { id, title, sql: '', result: null, running: false, page: 1, pageSize: state.pageSize }
  state.qTabs.push(tab)
  state.activeQueryTabId = id
  // 同步全局镜像（空白页）
  state.sql = ''
  state.result = null
  state.page = 1
  state.totalRows = 0
  state.pageSize = state.pageSize || 50
  // 切换后让编辑器显示新标签的内容
  nextTick(() => ensureSqlEditor())
}

function closeQueryTab(id: string) {
  const i = (state.qTabs || []).findIndex(t => t.id === id)
  if (i < 0) return
  const removingActive = state.qTabs[i].id === state.activeQueryTabId
  state.qTabs.splice(i, 1)
  if (!state.qTabs.length) {
    // 至少保留一个空标签
    const nid = cryptoRandomId()
    state.qTabs = [{ id: nid, title: nextTabTitle(), sql: '', result: null, running: false, page: 1, pageSize: state.pageSize }]
    state.activeQueryTabId = nid
    // 镜像
    state.sql = ''
    state.result = null
    state.page = 1
    state.totalRows = 0
  } else if (removingActive) {
    const next = state.qTabs[Math.max(0, i - 1)]
    state.activeQueryTabId = next.id
    // 镜像到全局
    state.sql = next.sql || ''
    state.result = (next as any).result || null
    state.page = Number((next as any).page || 1)
    state.pageSize = Number((next as any).pageSize || state.pageSize)
    state.totalRows = Number((next as any).totalRows || 0)
  }
  nextTick(() => ensureSqlEditor())
  }

  function setActiveTab(id: string) {
    if (!id || state.activeQueryTabId === id) return
    state.activeQueryTabId = id
    const at = (state.qTabs || []).find(t => t.id === id) as any
    if (at) {
      state.sql = at.sql || ''
      state.result = at.result || null
      state.page = Number(at.page || 1)
      state.pageSize = Number(at.pageSize || state.pageSize)
      state.totalRows = Number(at.totalRows || 0)
    }
    nextTick(() => ensureSqlEditor())
  }

  function cryptoRandomId(): string {
    try {
      // 浏览器安全随机
      const arr = new Uint32Array(2)
      crypto.getRandomValues(arr)
      return 'q' + arr[0].toString(36) + arr[1].toString(36)
    } catch {
      return 'q' + Math.random().toString(36).slice(2)
    }
  }

  // --- ui helpers ---
  function toggleDbDropdown() {
    if (!state.selectedConnId) return
    state.dbDropdownOpen = !state.dbDropdownOpen
    // 选中库数>=1 时，无论面板是否打开都保持树过滤
    state.forceTreeFilter = !!(Array.isArray(state.selectedDbs) && state.selectedDbs.length >= 1)
  }

  function onDbToggle(db: string, checked: boolean) {
    const i = state.selectedDbs.indexOf(db)
    if (checked) {
      if (i < 0) state.selectedDbs.push(db)
    } else {
      if (i >= 0) state.selectedDbs.splice(i, 1)
    }
    state.forceTreeFilter = !!(state.selectedDbs.length >= 1)
    // 若刚选到第一个库且尚未加载表，立即加载
    if (checked && !state.tables[db]) {
      loadTables(db)
    }
    // 设置活动库
    if (checked && !state.selectedDb) state.selectedDb = db
  }

  function clearDbSelection() {
    state.selectedDbs = []
    state.selectedDb = ''
    state.forceTreeFilter = false
  }

  function toggleLeftCollapsed() {
    state.leftCollapsed = !state.leftCollapsed
  }

  // --- pagination ---
  const totalPages: ComputedRef<number> = computed(() => {
    const total = Number(state.totalRows || 0)
    const ps = Math.max(1, Number(state.pageSize) || 50)
    return Math.max(1, Math.ceil(total / ps))
  })

  async function goToPage(p: number) {
    const tp = totalPages.value
    const next = Math.min(Math.max(1, Math.floor(Number(p) || 1)), tp)
    state.page = next
    const at = activeTab.value as any
    if (at) at.page = next
    // 翻页后重新执行上一次 SQL
    if (String((activeTab.value?.sql ?? state.sql) || '').trim()) {
      await executeSQL()
    }
  }

  return {
    state,
    filteredDatabases,
    filteredTables,
    initConsole,
    ensureSqlEditor,
    focusSqlEditor,
    executeSQL,
    stopExecution,
    viewPlan,
    beautifySQL,
    loadTables,
    appendTableToSQL,
    newQueryTab,
    closeQueryTab,
    // optional: for tab switching UI
    setActiveTab,
    toggleDbDropdown,
    onDbToggle,
    clearDbSelection,
    toggleLeftCollapsed,
    totalPages,
    goToPage,
    exportCSV,
    exportExcel,
  }
}
