<template>
  <div class="sql-next">
    <header class="hdr">
      <div class="title">SQL控制台（Next）</div>
      <div class="hdr-actions sticky" ref="toolbarActionsRef">
        <button class="icon-btn add" :disabled="running" @click="exec" title="执行"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></button>
        <button class="icon-btn warn" :disabled="!running" @click="stop" title="停止"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h12v12H6z"/></svg></button>
        <button class="icon-btn info" :disabled="running" @click="beautify" title="格式化"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z"/></svg></button>
        <button class="icon-btn" :disabled="running" @click="viewPlan" title="执行计划"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zM3 9h2V7H3v2zm4 8h2v-6H7v6zm4 0h2V5h-2v12zm4 0h2v-8h-2v8zm4 0h2v-4h-2v4z"/></svg></button>
        <button class="icon-btn" :disabled="running" @click="exportCSV" title="导出 CSV"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5v5h5v4zm-8.5 4.5H8l-1-1-1 1H4.5l2-2-2-2H6l1 1 1-1h1.5l-2 2 2 2zm3.5.5c-1.1 0-2-.9-2-2h1.5a.5.5 0 1 0 1 0c0-.3-.2-.5-.6-.7l-.4-.1c-1-.3-1.5-.9-1.5-1.7 0-1.1.9-2 2-2s2 .9 2 2h-1.5a.5.5 0 1 0-1 0c0 .2.2 .4 .6 .6l.4 .1c1 .3 1.5 1 1.5 1.8 0 1.1-.9 2-2 2zm4 .5-1.8-5H16l2 6h1l2-6h-1.2L18.5 18z"/></svg></button>
        <button class="icon-btn" :disabled="running" @click="exportExcel" title="导出 Excel"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M19 2H8a2 2 0 0 0-2 2v3h2V4h11v16H8v-3H6v3a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zM5 7H3l3.5 5L3 17h2l2-3.6L10 17h2L8.5 12 12 7H10L7.5 10.6 5 7z"/></svg></button>
      </div>
    </header>
    <div class="layout" :style="{ '--left-w': leftWidth + 'px' }">
    <!-- 左侧：三层树（实例->库->表） + 全局搜索 -->
    <aside class="left">
        <div class="tree" role="tree">
          <div class="inst" v-for="inst in instances" :key="'i-'+inst.id">
            <div class="inst-hd" @click="toggleConn(inst.id)" @mouseenter="hoverInst=inst.id" @mouseleave="hoverInst=''">
              <span class="arrow" :class="{open: expandConn[inst.id]}" aria-hidden="true">›</span>
              <span class="label" :title="inst.ip + ':' + inst.port">
                {{ inst.description || (inst.ip + ':' + inst.port) || ('#' + inst.id) }}
              </span>
              <button v-show="hoverInst===inst.id || hasInstFilter(inst.id)" class="mini filter" :class="{ active: hasInstFilter(inst.id) }" title="选择实例库" @click.stop="openInstFilter(inst, $event)">⚙</button>
            </div>
            <!-- 实例库过滤面板（按钮同水平位置显示，包含搜索框；鼠标移出自动关闭） -->
            <div
              v-if="instFilterVisible===inst.id"
              class="panel inst-panel"
              :style="{ left: instPanelPos.left + 'px', top: instPanelPos.top + 'px' }"
              @mousedown.stop
              @mouseleave="instFilterVisible=''"
            >
              <div class="ph-search">
                <span class="ico" aria-hidden="true">🔍</span>
                <input v-model.trim="instSearch" placeholder="搜索数据库..." />
                <button class="clear" :title="'清空所选库'" @click="clearInstSelected(inst.id)">🧹</button>
              </div>
              <div class="plist">
                <label class="opt" v-for="db in (filterInstDbs(inst.id))" :key="'p-'+inst.id+'-'+db">
                  <input type="checkbox" :checked="isDbSelected(inst.id, db)" @change="onDbSelect(inst.id, db, $event)">
                  <span>{{ db }}</span>
                </label>
              </div>
            </div>
            <ul v-show="expandConn[inst.id]" class="dbs">
              <li class="db" v-for="db in filteredDbList(inst.id)" :key="'db-'+inst.id+'-'+db">
                <div class="db-hd" @click="toggleDb(inst.id, db)" @mouseenter="hoverDb=inst.id+':'+db" @mouseleave="onDbMouseLeave(inst.id, db)">
                  <span class="arrow" :class="{open: !!expandDbByConn[inst.id]?.[db]}" aria-hidden="true">›</span>
                  <span class="label" :title="db">{{ db }}</span>
                  <button
                    v-show="hoverDb===inst.id+':'+db || !!dbFilterTextByKey[keyOf(inst.id, db)] || dbFilterVisibleKey===keyOf(inst.id, db)"
                    class="mini filter"
                    :class="{ active: !!dbFilterTextByKey[keyOf(inst.id, db)] }"
                    :title="dbFilterTextByKey[keyOf(inst.id, db)] ? '已过滤：' + dbFilterTextByKey[keyOf(inst.id, db)] : '过滤该库的表'"
                    @click.stop="showDbFilterPopup(inst.id, db, $event)"
                  >🔍</button>
                  <input v-if="dbFilterVisibleKey==='__inline__never__'" class="db-filter-input" />
                </div>
                <ul v-show="expandDbByConn[inst.id]?.[db]" class="tbls">
                  <li class="tbl" v-for="t in filteredTablesForDisplay(inst.id, db)" :key="'t-'+inst.id+'-'+db+'-'+t" @click="appendSnip(db, t)">{{ t }}</li>
                  <li class="muted" v-if="loadingKey(inst.id, db)">加载中...</li>
                  <li class="muted" v-else-if="emptyKey(inst.id, db)">无表</li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
        <div class="gsearch">
          <div class="searchbox">
            <span class="ico" aria-hidden="true">🔍</span>
            <input v-model.trim="globalDbSearch" placeholder="搜索" />
            <button class="mini action" title="清除所有过滤" @click="clearAllDbFilters">🧹</button>
            <button class="mini action" title="折叠菜单" @click="collapseAllDbs">📂</button>
          </div>
        </div>
      </aside>
      <div class="vsplit" @mousedown="startDrag"></div>
      <!-- 右侧：编辑器在上，结果在下（保持与旧页一致的按钮组） -->
      <main class="right" :style="{ '--left-w': leftWidth + 'px' }">
        <!-- 浮动库表过滤输入框：允许跨出左侧区域显示在右侧 -->
        <input
          v-if="dbFilterPopup.show"
          class="db-filter-float"
          :style="{ left: dbFilterPopup.left + 'px', top: dbFilterPopup.top + 'px' }"
          :value="popupInputValue"
          @input="onPopupInput"
          @change="onPopupChange"
          @keydown.enter.prevent="onPopupConfirm"
          @mouseenter="popupHover = true"
          @mouseleave="popupHover = false; if(!dbFilterTextByKey[dbFilterPopup.key]) dbFilterPopup.show=false"
          placeholder="搜索"
        />
        <div class="tabs">
          <SqlTabs :ctx="tq" />
          <ConfirmDialog
            :visible="confirmCloseVisible"
            :text="'确定要关闭当前 SQL 标签吗？未保存的内容将丢失。'"
            :meta="{ type: 'SQL 标签', env: connInfo }"
            @confirm="performCloseTab"
            @cancel="cancelCloseTab"
          />
        </div>
        <!-- 关闭确认：Element 优先，必要时回退到自定义弹窗（以防样式/层级异常） -->
        <!-- 回退用的自定义弹窗先移除，确保优先体验 Element 样式 -->
        <div class="editor-wrap" ref="editorWrapRef" :style="{ height: editorHeight + 'px', marginTop: '0px' }">
          <div class="editor" ref="editorRef" :style="{ height: editorHeight + 'px' }"></div>
        </div>
        <div class="hsplit" @mousedown="startHDrag"></div>
        <div class="result">
          <div class="rbody" :class="{ 'table-mode': result && result.type==='table' }">
            <div v-if="result && result.type==='table'" class="table-holder">
              <ResultTable />
            </div>
            <pre v-else-if="result && result.type==='text'" class="txt">{{ result.text }}</pre>
            <div v-else class="info muted placeholder">在此显示查询结果或执行信息</div>
          </div>
          <!-- 底部横向滚动条（与旧页保持一致） -->
          <div class="x-scroll" ref="xScrollRef" @scroll="onXScroll" v-show="result && result.type==='table'">
            <div class="spacer" :style="{ width: spacerWidth + 'px', height: '1px' }"></div>
          </div>
          <div class="tq-pagination" v-if="result && result.type==='table'">
            <button class="icon-btn" :disabled="page<=1" @click="goToPage(page-1)" title="上一页">‹</button>
            <span class="muted">第</span>
            <input type="number" v-model.number="pageInput" @keyup.enter="handlePageJump" min="1" :max="totalPages" style="width:70px;height:28px" />
            <span class="muted">/ {{ totalPages }} 页</span>
            <button class="icon-btn" :disabled="page>=totalPages" @click="goToPage(page+1)" title="下一页">›</button>
            <span class="muted" style="margin-left:12px">每页</span>
            <select :value="pageSize" @change="handlePageSizeChange($event)" title="每页条数">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span class="muted">条，共 {{ totalRows || 0 }} 条</span>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUpdated, onBeforeUnmount, provide, nextTick, watchEffect } from 'vue'
import api from '../../api'
import SqlTabs from './SqlTabs.vue'
import ResultTable from './ResultTable.vue'
import ConfirmDialog from '../conn/ConfirmDialog.vue'
// CodeMirror（与旧页一致的依赖）
import { EditorState } from '@codemirror/state'
import { EditorView, keymap, highlightActiveLine, lineNumbers } from '@codemirror/view'
import { sql, MySQL } from '@codemirror/lang-sql'
import { syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language'
import { autocompletion, CompletionContext, completionKeymap, startCompletion } from '@codemirror/autocomplete'

// URL 参数（与旧独立页一致）
const sp = new URLSearchParams(window.location.search)
const raw = sp.get('connId') || sp.get('connectionId') || sp.get('conn_id') || ''
const connId = computed(() => { const n = Number(raw); return Number.isFinite(n)&&n>0 ? n : raw })
const initDb = computed(()=> sp.get('database') || sp.get('db') || sp.get('schema') || '')

// 头部连接信息
const connInfo = ref('')

// 左侧三层树状态
const instances = ref<any[]>([])
const expandConn = reactive<Record<string|number, boolean>>({})
const expandDbByConn = reactive<Record<string|number, Record<string, boolean>>>({})
const dbsByConn = reactive<Record<string|number, string[]>>({})
const tablesByKey = reactive<Record<string, string[]>>({})
const tablesLoading = reactive<Record<string, boolean>>({})
const selectedDbByConn = reactive<Record<string|number, Set<string>>>({})
const instFilterVisible = ref<string|number>('')
const instPanelPos = reactive<{left:number;top:number}>({ left: 0, top: 0 })
const instSearch = ref('')
function hasInstFilter(id:any){ const set = selectedDbByConn[id]; return !!(set && set.size>0) }
const globalDbSearch = ref('')
const hoverInst = ref<string|number>('')
const hoverDb = ref<string>('')
// 数据库过滤交互：每个库独立的过滤文本与显示状态
const dbFilterTextByKey = reactive<Record<string, string>>({})
const dbFilterVisibleKey = ref<string>('')
// 浮动输入框定位数据
const dbFilterPopup = reactive<{ show:boolean; left:number; top:number; key:string }>({ show:false, left:0, top:0, key:'' })
const popupHover = ref(false)
const leftWidth = ref(270)

// 右侧
const editorWrapRef = ref<HTMLElement|null>(null)
const editorRef = ref<HTMLElement|null>(null)
let cmView: any = null
const running = ref(false)
let currentAbort: AbortController | null = null
const result = ref<any|null>(null)
const currentDb = ref('')
const editorHeight = ref(150)
const editorHeightCommitted = ref(150)
const toolbarActionsRef = ref<HTMLElement | null>(null)
let toolbarObserver: MutationObserver | null = null
let toolbarObservedEl: HTMLElement | null = null
let editorResizeObserver: ResizeObserver | null = null

function setupToolbarObserver(){
  try {
    const target = toolbarActionsRef.value
    if (!target) return
    if (!toolbarObserver) {
      toolbarObserver = new MutationObserver(() => {
        try {
          target.classList.add('sticky')
          target.style.visibility = 'visible'
          target.style.opacity = '1'
          target.style.pointerEvents = 'auto'
        } catch {}
      })
    }
    if (toolbarObservedEl !== target) {
      toolbarObserver.disconnect()
      toolbarObservedEl = target
      target.classList.add('sticky')
      target.style.visibility = 'visible'
      target.style.opacity = '1'
      target.style.pointerEvents = 'auto'
      toolbarObserver.observe(target, { attributes: true, attributeFilter: ['style'], attributeOldValue: true })
    }
  } catch {}
}

onBeforeUnmount(() => {
  if (toolbarObserver) {
    toolbarObserver.disconnect()
    toolbarObservedEl = null
  }
})

// 结果与分页
const page = ref(1)
const pageSize = ref(50)
const totalRows = ref(0)
const pageInput = ref(1)
const totalPages = computed(()=>{ const t=Number(totalRows.value||0); const ps=Number(pageSize.value||1); return Math.max(1, Math.ceil(t/Math.max(1,ps))) })

// ResultTable 上下文（与旧页一致的头部锁定/排序/同步滚动逻辑）
const tq = reactive<any>({
  result: computed(()=> result.value),
  tableColWidths: [] as number[],
  bodyTableWidth: 0,
  freezeCount: 0,
  freezeLefts: [] as number[],
  sortKey: '',
  sortDir: 'asc',
  page,
  pageSize,
  isRunning: computed(()=> running.value),
  qTabs: [] as any[],
  activeQueryTabId: '' as any
})
const tqHeadTableRef = ref<any>(null)
const tqBodyTableRef = ref<any>(null)
const tqScrollXRef = ref<any>(null)
const tqBodyRef = ref<any>(null)
const xScrollRef = ref<HTMLElement|null>(null)
const bodyScrollRef = ref<HTMLElement|null>(null)
const spacerWidth = ref(1600)

function updateSpacerWidth(){
  try {
    const bodyTable = tqBodyTableRef.value as HTMLTableElement | null
    const body = tqBodyRef.value as HTMLElement | null
    const widthFromDom = bodyTable ? bodyTable.scrollWidth : 0
    const widthFromBody = body ? body.scrollWidth : 0
    const computedCols = tq.tableColWidths.reduce((a: number, b: number) => a + b, 0)
    const finalWidth = Math.max(widthFromDom, widthFromBody, computedCols, 1600)
    spacerWidth.value = finalWidth
    tq.bodyTableWidth = finalWidth
    // 仅在内容超出时显示底部横向滚动条
    try {
      const xs = xScrollRef.value as HTMLElement | null
      if (xs && body) {
        const needX = (body.scrollWidth - 1) > body.clientWidth
        xs.style.display = needX ? 'block' : 'none'
      }
    } catch {}
  } catch {
    const fallback = Math.max(tq.bodyTableWidth || 0, 1600)
    spacerWidth.value = fallback
    tq.bodyTableWidth = fallback
  }
  try {
    const wrap = editorWrapRef.value
    if (wrap) {
      wrap.style.overflow = 'visible'
      wrap.style.position = 'relative'
    }
  } catch {}
}

/**
 * 计算结果表格的每列宽度（带中文注释）
 * - 优先依据第一行数据单元格的实际宽度
 * - 再叠加表头文本的滚动宽度，保证"列标题完整可见"，不被截断
 * - 取两者更大值作为该列最终宽度
 */
function computeColWidths(){
  try {
    const bodyTable = tqBodyTableRef.value as HTMLTableElement | null
    const headTable = tqHeadTableRef.value as HTMLTableElement | null
    const colCount = (result.value?.columns || []).length
    let widths: number[] = []

    if (!bodyTable) {
      widths = (result.value?.columns || []).map(() => 140)
    } else {
      const firstRowCells = Array.from(bodyTable.querySelectorAll('tbody tr:first-child td')) as HTMLElement[]
      if (firstRowCells.length) {
        widths = firstRowCells.map((cell: any) => Math.max(120, Math.ceil(Number(cell?.offsetWidth || cell?.clientWidth || 120))))
      } else {
        widths = (result.value?.columns || []).map(() => 140)
      }
    }

    // 叠加表头文本实际所需宽度，保证标题不被截断
    try {
      if (headTable && colCount) {
        const ths = Array.from(headTable.querySelectorAll('thead th')) as HTMLElement[]
        for (let i = 0; i < colCount; i++) {
          const th = ths[i] as HTMLElement | undefined
          if (!th) continue
          const inner = th.querySelector('.th-inner') as HTMLElement | null
          const need = Math.ceil(Number(inner?.scrollWidth || th.scrollWidth || 0)) + 20 // 文本+操作按钮+resizer 余量
          widths[i] = Math.max(widths[i] || 120, Math.max(120, need))
        }
      }
    } catch {}

    tq.tableColWidths = widths
    tq.bodyTableWidth = widths.reduce((a: number, b: number) => a + b, 0)
  } catch {
    const cols = (result.value?.columns || []).map(() => 140)
    tq.tableColWidths = cols
    tq.bodyTableWidth = cols.reduce((a, b) => a + b, 0)
  }
  nextTick(() => {
    updateSpacerWidth()
    syncHorizontalScroll()
  })
}
function adjustHeaderGutter(){ /* 已在子组件内处理 */ }
function getDisplayedRows(){ try{ const rows = (result.value?.data)||[]; const start=(page.value-1)*pageSize.value; return rows.slice(start, start+pageSize.value) } catch { return [] } }
function headerLockClick(i:number){ tq.freezeCount = (i < tq.freezeCount) ? i : (i+1) ; const lefts:number[]=[]; let acc=0; for(let k=0;k<tq.freezeCount;k++){ acc += Number(tq.tableColWidths[k]||0); lefts[k]=acc-Number(tq.tableColWidths[k]||0) } tq.freezeLefts = lefts }
function toggleSort(col:string){ if (tq.sortKey===col) { tq.sortDir = tq.sortDir==='asc'?'desc':'asc' } else { tq.sortKey=col; tq.sortDir='asc' } try { const rows = (result.value?.data)||[]; const dir = tq.sortDir==='asc'?1:-1; const sorted = [...rows].sort((a:any,b:any)=> (a?.[col] > b?.[col] ? dir : -dir)); result.value = { ...result.value, data: sorted } } catch {} }
function startColResize(i:number, e:MouseEvent){ const startX=e.clientX; const startW = Number(tq.tableColWidths[i]||140); const onMove=(ev:MouseEvent)=>{ const w=Math.max(80, startW + ev.clientX - startX); tq.tableColWidths.splice(i,1,w); tq.bodyTableWidth = tq.tableColWidths.reduce((a:number,b:number)=>a+b,0) }; const onUp=()=>{ window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp) }; window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp, {once:true}) }
function onBodyScroll(ev?: Event){
  try {
    const body = (ev?.target as HTMLElement) || (tqBodyRef.value as HTMLElement | null)
    if (!body) return
    syncHorizontalScroll(body.scrollLeft)
    syncBodyScroll(body.scrollTop)
    updateSpacerWidth()
  } catch {}
}

function resetTableScroll(){
  try {
    const body = tqBodyRef.value as HTMLElement | null
    if (body) {
      body.scrollTop = 0
    }
  } catch {}
  syncHorizontalScroll(0)
  syncBodyScroll(0)
  updateSpacerWidth()
}

function syncBodyScroll(targetTop?: number){
  try {
    const body = tqBodyRef.value as HTMLElement | null
    const ext = bodyScrollRef.value as HTMLElement | null
    if (!body || !ext) return
    const top = typeof targetTop === 'number' ? targetTop : body.scrollTop
    if (typeof targetTop === 'number' && body.scrollTop !== targetTop) body.scrollTop = targetTop
    if (ext.scrollTop !== top) ext.scrollTop = top
  } catch {}
}

function syncHorizontalScroll(targetLeft?: number){
  try {
    const body = tqBodyRef.value as HTMLElement | null
    const xs = xScrollRef.value as HTMLElement | null
    const head = tqScrollXRef.value as HTMLElement | null
    const left = typeof targetLeft === 'number' ? targetLeft : Number(body?.scrollLeft || 0)
    if (typeof targetLeft === 'number' && body && body.scrollLeft !== targetLeft) body.scrollLeft = targetLeft
    if (xs && xs.scrollLeft !== left) xs.scrollLeft = left
    if (head && head.scrollLeft !== left) head.scrollLeft = left
  } catch {}
}

provide('tqCtx', {
  tq,
  tqHeadTableRef,
  tqBodyTableRef,
  tqScrollXRef,
  tqBodyRef,
  bodyScrollRef,
  editorWrapRef,
  computeColWidths,
  adjustHeaderGutter,
  getDisplayedRows,
  headerLockClick,
  toggleSort,
  startColResize,
  onBodyScroll,
  resetTableScroll,
  // 供 SqlTabs 使用（与独立窗口保持一致的方法名）
  newQueryTab: () => newTab(),
  closeQueryTab: (id: string) => requestCloseTab(id),
  activateQueryTab: (id: string) => switchTab(id)
})

function toggleConn(id:any){ expandConn[id] = !expandConn[id]; if (expandConn[id] && !dbsByConn[id]) loadDatabasesByConn(id) }
function toggleDb(id:any, db:string){ if (!expandDbByConn[id]) expandDbByConn[id] = {}; expandDbByConn[id][db] = !expandDbByConn[id][db]; if (expandDbByConn[id][db]) { currentDb.value = db; loadTablesByConnDb(id, db) } }

function openInstFilter(inst:any, ev?: MouseEvent){
  instFilterVisible.value = inst.id
  if (!dbsByConn[inst.id]) loadDatabasesByConn(inst.id)
  if (!selectedDbByConn[inst.id]) selectedDbByConn[inst.id] = new Set<string>()
  try {
    const btn = ev?.currentTarget as HTMLElement | null
    if (btn) {
      const rect = btn.getBoundingClientRect()
      // 与按钮同水平位置显示（靠近右侧，向下 4px）
      instPanelPos.left = rect.right + 8
      instPanelPos.top = rect.top + window.scrollY + 4
    } else {
      instPanelPos.left = leftWidth.value + 12
      instPanelPos.top = 0
    }
  } catch {}
  nextTick(()=>{
    try {
      const input = document.querySelector('.inst-panel .ph-search input') as HTMLInputElement | null
      input && input.focus()
    } catch {}
  })
}
function filterInstDbs(id:any){
  const kw = (instSearch.value||'').trim().toLowerCase()
  const all = dbsByConn[id] || []
  if (!kw) return all
  return all.filter((n:string)=> n.toLowerCase().includes(kw))
}
function isDbSelected(id:any, db:string){ return !!selectedDbByConn[id]?.has(db) }
function onDbSelect(id:any, db:string, ev:Event){ const on=(ev.target as HTMLInputElement).checked; if(!selectedDbByConn[id]) selectedDbByConn[id]=new Set<string>(); if(on) selectedDbByConn[id].add(db); else selectedDbByConn[id].delete(db) }
function filteredDbList(id:any){ const all = dbsByConn[id]||[]; const sel=selectedDbByConn[id]; const tokens=(globalDbSearch.value||'').trim().toLowerCase().split(/\s+/).filter(Boolean); return all.filter(db=>{ if(sel&&sel.size>0&&!sel.has(db)) return false; if(!tokens.length) return true; const s=db.toLowerCase(); return tokens.some(t=>s.includes(t)) }) }
// 保留旧方法名：为了兼容引用，如有调用则改为展示浮层
function openDbFilter(id:any, db:string){ showDbFilterPopup(id, db) }
// 改为行内输入：显示输入框并保持图标可见
function keyOf(id:any, db:string){ return `${id}::${db}` }
function openDbFilterInline(id:any, db:string){ dbFilterVisibleKey.value = keyOf(id, db) }
// 打开浮动输入框：根据按钮位置计算坐标，让其可跨出左栏
function showDbFilterPopup(id:any, db:string, ev?: MouseEvent){
  const key = keyOf(id, db)
  dbFilterVisibleKey.value = key
  try {
    const btn = ev?.currentTarget as HTMLElement | null
    if (btn) {
      const rect = btn.getBoundingClientRect()
      dbFilterPopup.show = true
      dbFilterPopup.left = rect.right + 8 // 在按钮右侧 8px
      dbFilterPopup.top = rect.top - 2
      dbFilterPopup.key = key
      popupInputValue.value = dbFilterTextByKey[key] || ''
      nextTick(() => {
        const el = document.querySelector('.db-filter-float') as HTMLInputElement | null
        try { el && el.focus() } catch {}
      })
    }
  } catch {}
}
const popupInputValue = ref('')
function onPopupInput(e: Event){ popupInputValue.value = (e.target as HTMLInputElement).value }
function onPopupChange(){ dbFilterTextByKey[dbFilterPopup.key] = popupInputValue.value.trim(); if(!dbFilterTextByKey[dbFilterPopup.key]) { dbFilterPopup.show=false; dbFilterVisibleKey.value=''} }
function onPopupConfirm(){
  // 提交并展开当前库
  dbFilterTextByKey[dbFilterPopup.key] = (popupInputValue.value || '').trim()
  // 解析 key -> id,db
  try {
    const [idStr, db] = dbFilterPopup.key.split('::')
    const id:any = isNaN(Number(idStr)) ? idStr : Number(idStr)
    if (!expandDbByConn[id]) expandDbByConn[id] = {}
    expandDbByConn[id][db] = true
  } catch {}
  // 关闭浮窗
  dbFilterPopup.show = false
}
function onDbFilterInput(id:any, db:string, e:Event){
  const key = keyOf(id, db)
  const txt = String((e.target as HTMLInputElement)?.value || '').trim()
  dbFilterTextByKey[key] = txt
  const all = tablesByKey[key] || []
  if (!txt) { // 恢复原始（若无缓存则保持）
    // 不改 tablesByKey，本地显示时用 filteredTablesFor 结合文本过滤
  }
}
function onDbMouseLeave(id:any, db:string){
  const key = keyOf(id, db)
  hoverDb.value = ''
  // 若无过滤文本则隐藏输入框和图标（允许鼠标移至浮窗时不立即关闭）
  if (!dbFilterTextByKey[key]) {
    dbFilterVisibleKey.value = ''
    setTimeout(() => {
      if (!popupHover.value && (!dbFilterPopup.key || !dbFilterTextByKey[dbFilterPopup.key])) {
        dbFilterPopup.show = false
      }
    }, 120)
  }
}
function clearInstSelected(id:any){ if (selectedDbByConn[id]) selectedDbByConn[id].clear() }
function filteredTablesFor(id:any, db:string){ const key=`${id}::${db}`; return tablesByKey[key]||[] }
// 增强：若存在过滤文本，则基于缓存结果做一次前端过滤
function filteredTablesForDisplay(id:any, db:string){
  const key = keyOf(id, db)
  const base = tablesByKey[key] || []
  const txt = (dbFilterTextByKey[key] || '').toLowerCase().trim()
  if (!txt) return base
  const tokens = txt.split(/\s+/).filter(Boolean)
  if (!tokens.length) return base
  return base.filter(t => tokens.some(k => String(t).toLowerCase().includes(k)))
}
function clearAllDbFilters(){
  // 清除所有库的过滤文本，并隐藏浮窗
  for (const k of Object.keys(dbFilterTextByKey)) delete dbFilterTextByKey[k]
  dbFilterPopup.show = false
  dbFilterVisibleKey.value = ''
  // 同时清除“实例级别的库选择过滤”（全局清理）
  try {
    for (const id in selectedDbByConn) {
      const set = selectedDbByConn[id]
      if (set && typeof set.clear === 'function') set.clear()
    }
  } catch {}
}
function collapseAllDbs(){
  // 折叠到实例级：关闭所有实例与其下数据库展开
  for (const id in expandConn) expandConn[id] = false
  for (const id in expandDbByConn) {
    const m = expandDbByConn[id]
    if (m) for (const db in m) m[db] = false
  }
  instFilterVisible.value = ''
}
function loadingKey(id:any, db:string){ return !!tablesLoading[`${id}::${db}`] }
function emptyKey(id:any, db:string){ const key=`${id}::${db}`; const arr=tablesByKey[key]; return Array.isArray(arr) && arr.length===0 }

async function loadConnections(){ try{ const {data}=await api.get('/connections'); instances.value=Array.isArray(data)?data:[] }catch{ instances.value=[] } }
async function loadConnInfo(){ try{ const {data}=await api.get(`/connections/${connId.value}`); connInfo.value = `${data.user}@${data.ip}:${data.port} (${data.description||data.ip+':'+data.port||('#'+data.id)})` }catch{ connInfo.value='' } }
async function loadDatabasesByConn(id:any){ try{ const {data}=await api.get(`/connections/${id}/databases`); dbsByConn[id]=Array.isArray(data)?data:[] }catch{ dbsByConn[id]=dbsByConn[id]||[] } }
async function loadTablesByConnDb(id:any, db:string){
  const key=`${id}::${db}`; tablesLoading[key]=true
  try{
    // 优先新接口
    try{
      const {data}=await api.get(`/connections/${id}/databases/${encodeURIComponent(db)}/tables`)
      if (Array.isArray(data)) { tablesByKey[key]=data; return }
    }catch{}
    // 回退旧接口（与现有后端兼容）
    const { data } = await api.get('/ticket/tables', { params: { connId: id, db, database: db, schema: db } })
    tablesByKey[key] = Array.isArray(data) ? data : []
  }catch{ tablesByKey[key]=tablesByKey[key]||[] }
  finally{ tablesLoading[key]=false }
}

function startDrag(e:MouseEvent){ const sx=e.clientX, sw=leftWidth.value; const onMove=(ev:MouseEvent)=>{ leftWidth.value=Math.max(180, Math.min(560, sw + ev.clientX - sx)) }; const onUp=()=>{ window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp)}; window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp, {once:true}) }

function startHDrag(e:MouseEvent){ const sy=e.clientY, sh=editorHeight.value; const onMove=(ev:MouseEvent)=>{ const nh = Math.max(100, Math.min(600, sh + ev.clientY - sy)); editorHeight.value = nh; try{ cmView && cmView.requestMeasure && cmView.requestMeasure() }catch{} }; const onUp=()=>{ editorHeightCommitted.value = editorHeight.value; refreshEditorLayout(); window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp)}; window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp, {once:true}) }

function appendSnip(db:string, tbl:string){
  currentDb.value = db
  const snip = `-- ${db}.${tbl}\nSELECT * FROM ${db}.${tbl} LIMIT 100;\n`
  try {
    if (cmView) {
      const doc = cmView.state.doc.toString()
      const prefix = (doc && !/\n$/.test(doc)) ? '\n' : ''
      cmView.dispatch({ changes: { from: doc.length, to: doc.length, insert: prefix + snip } })
      ;(globalThis as any).__next_sql_text = cmView.state.doc.toString()
      cmView.focus()
      return
    }
  } catch {}
}
/**
 * 执行当前标签页的 SQL
 * - 成功后会把"结果与分页状态"写回到当前标签对象，做到"每个标签互不影响"
 */
async function exec(){
  const txtGlobal = (globalThis as any).__next_sql_text
  const sql = (typeof txtGlobal==='string' && txtGlobal.trim()) ? txtGlobal : ''
  if(!sql) return
  // 若已有执行在进行，则直接返回，防止并发执行
  if (running.value) return
  ensureActionBarVisible()
  page.value = Math.max(1, page.value)
  running.value=true; result.value={ type:'text', text:'执行中...' }
  // 创建取消控制器
  try { if (currentAbort) currentAbort.abort() } catch {}
  currentAbort = new AbortController()
  try{
    const payload:any = { connId: connId.value, sql, page: page.value, pageSize: pageSize.value }
    if (currentDb.value) payload.database = currentDb.value
    const {data}=await api.post('/ticket/execute', payload, { signal: (currentAbort as any)?.signal })
    if (data && Array.isArray(data.data) && Array.isArray(data.columns)) {
      result.value={ type:'table', data:data.data, columns:data.columns }
      totalRows.value = Number(data.total || data.count || data.totalRows || data.data.length || 0)
      pageInput.value = page.value
    } else if (Array.isArray(data)) {
      const cols = data.length ? Object.keys(data[0]) : []
      result.value={ type:'table', data, columns: cols }
      totalRows.value = data.length
      pageInput.value = page.value
    } else if (data && Array.isArray(data.rows) && Array.isArray(data.columns)) {
      result.value={ type:'table', data:data.rows, columns:data.columns }
      totalRows.value = Number(data.total || data.count || data.rows.length || 0)
      pageInput.value = page.value
    } else if (typeof data==='string') {
      result.value={ type:'text', text:data }
    } else if (data && (data.message || data.text)) {
      result.value={ type:'text', text: data.message || data.text }
    } else {
      result.value={ type:'text', text: '执行完成' }
    }
  }catch(e:any){
    const aborted = (e && (e.name==='CanceledError' || e.name==='AbortError'))
    result.value={ type:'text', text: aborted ? '已停止执行' : (e?.response?.data?.detail || e?.message || '执行失败') }
  } finally{ running.value=false; try{ currentAbort = null }catch{} }
  await nextTick()
  computeColWidths()
  resetTableScroll()
  updateSpacerWidth()
  await refreshEditorLayout()
  // 执行后保持 tabs 吸顶与层级，且编辑器紧贴其下，不允许编辑器层级超过 tabs
  try {
    const tabsEl = document.querySelector('.tabs') as HTMLElement | null
    const editorWrap = editorWrapRef.value
    if (tabsEl) { tabsEl.style.position = 'sticky'; tabsEl.style.top = '0px'; tabsEl.style.zIndex = '10000' }
    if (editorWrap) { editorWrap.style.marginTop = '0px'; editorWrap.style.zIndex = '1' }
  } catch {}
  const active = tabs.find(t => t.id === activeTab.value)
  if (active) {
    active.dirty = false
    active.result = result.value
    active.page = page.value
    active.pageSize = pageSize.value
    active.totalRows = totalRows.value
  }
  ensureActionBarVisible()
  setTimeout(() => ensureActionBarVisible(), 0)
}
function stop(){
  try { currentAbort && currentAbort.abort() } catch {}
  running.value=false
  ensureActionBarVisible()
  setTimeout(() => ensureActionBarVisible(), 0)
}
function viewPlan(){ /* 保留占位，与旧页一致 */ }
function beautify(){ try{ if(!cmView) return; let s=cmView.state.doc.toString(); s=s.replace(/[\t ]+/g,' ').replace(/\s*;\s*/g,';\n').replace(/\n{3,}/g,'\n\n').trim()+'\n'; cmView.dispatch({ changes:{ from:0, to: cmView.state.doc.length, insert: s } }); (globalThis as any).__next_sql_text = s }catch{} }

// 保留分页工具函数
function goToPage(p:number){ const tp=totalPages.value; const n=Math.min(tp, Math.max(1, Number(p)||1)); if(n===page.value) return; page.value=n; pageInput.value=n; exec() }
function handlePageJump(){ goToPage(pageInput.value as any) }
function handlePageSizeChange(e:Event){ const v=Number((e.target as HTMLSelectElement)?.value||pageSize.value); if(!Number.isFinite(v)||v<=0) return; pageSize.value=v; page.value=1; pageInput.value=1; exec() }

function onXScroll(){
  try {
    const body = tqBodyRef.value as HTMLElement | null
    const xs = xScrollRef.value as HTMLElement | null
    const head = tqScrollXRef.value as HTMLElement | null
    if (body && xs && body.scrollLeft !== xs.scrollLeft) body.scrollLeft = xs.scrollLeft
    if (head && xs && head.scrollLeft !== xs.scrollLeft) head.scrollLeft = xs.scrollLeft
  } catch {}
}

function ensureActionBarVisible(){
  setupToolbarObserver()
  try {
    const wrap = editorWrapRef.value
    if (wrap) {
      wrap.style.position = 'relative'
      wrap.style.overflow = 'visible'
    }
  } catch {}
}

function syncEditorScrollerOverflow(){
  try {
    const host = editorRef.value as HTMLElement | null
    if (!host) return
    const scroller = host.querySelector('.cm-scroller') as HTMLElement | null
    const content = host.querySelector('.cm-content') as HTMLElement | null
    if (!scroller || !content) return
    const needX = content.scrollWidth > scroller.clientWidth + 1
    scroller.style.overflowX = needX ? 'auto' : 'hidden'
    scroller.style.overflowY = 'auto'
  } catch {}
}

async function refreshEditorLayout(){
  if (editorHeight.value !== editorHeightCommitted.value) {
    editorHeight.value = editorHeightCommitted.value
  }
  await nextTick()
  try { cmView && cmView.requestMeasure && cmView.requestMeasure() } catch {}
  ensureActionBarVisible()
  syncEditorScrollerOverflow()
}

// 标签页
type Tab = {
  id: string
  title: string
  text: string
  dirty?: boolean
  result?: any | null
  page?: number
  pageSize?: number
  totalRows?: number
}
const tabs = reactive<Tab[]>([])
const activeTab = ref('')
// 关闭标签确认弹窗状态
const confirmCloseVisible = ref(false)
const closingTabId = ref('')
function newTab(){
  const n = tabs.length + 1
  const t:Tab = { id: String(Date.now()) + '-' + n, title: `SQL ${n}`, text: '', result: null, page: 1, pageSize: 50, totalRows: 0 }
  tabs.push(t)
  activeTab.value = t.id
  if (cmView) {
    cmView.dispatch({ changes:{ from:0, to: cmView.state.doc.length, insert: '' } })
    ;(globalThis as any).__next_sql_text = ''
  }
  // 重置全局呈现为该标签的状态
  result.value = null
  page.value = 1
  pageInput.value = 1
  pageSize.value = 50
  totalRows.value = 0
  refreshEditorLayout(); ensureActionBarVisible(); setTimeout(() => ensureActionBarVisible(), 0)
}
function reallyCloseTab(id:string){
  const idx = tabs.findIndex(t=>t.id===id)
  if (idx<0) return
  const wasActive = tabs[idx].id===activeTab.value
  tabs.splice(idx,1)
  if (!tabs.length) { newTab(); return }
  if (wasActive) { const next = tabs[Math.max(0, idx-1)]; switchTab(next.id) }
}
function requestCloseTab(id:string){ closingTabId.value = id; confirmCloseVisible.value = true }
function performCloseTab(){ const id = closingTabId.value; confirmCloseVisible.value = false; if (id) reallyCloseTab(id); closingTabId.value = '' }
function cancelCloseTab(){ confirmCloseVisible.value = false; closingTabId.value = '' }
function switchTab(id:string){
  const t = tabs.find(x=>x.id===id)
  if (!t) return
  activeTab.value = id
  if (cmView) {
    cmView.dispatch({ changes:{ from:0, to: cmView.state.doc.length, insert: t.text||'' } })
    ;(globalThis as any).__next_sql_text = t.text||''
    try { cmView.focus() } catch {}
  }
  // 恢复该标签自己的结果与分页
  result.value = t.result ?? null
  page.value = Number(t.page || 1)
  pageInput.value = page.value
  pageSize.value = Number(t.pageSize || 50)
  totalRows.value = Number(t.totalRows || 0)
  // 刷新表格宽度与滚动
  refreshEditorLayout(); ensureActionBarVisible(); setTimeout(() => { computeColWidths(); resetTableScroll(); updateSpacerWidth(); ensureActionBarVisible(); try{ cmView && cmView.focus() }catch{}; }, 0)
}
function updateActiveTabText(txt:string){ const t = tabs.find(x=>x.id===activeTab.value); if (t) { t.text = txt; t.dirty = true } }

// 将本地 tabs 同步到 tq（供 SqlTabs 复用旧样式）
watchEffect(() => {
  tq.qTabs = tabs.map(t => ({ id: t.id, title: t.title, ui: { dirty: !!t.dirty, disabled: running.value } }))
  tq.activeQueryTabId = activeTab.value
})

// 兼容 SqlTabs 调用的方法
;(tq as any).activateQueryTab = (id:string) => switchTab(id)
;(tq as any).newQueryTab = () => newTab()
;(tq as any).closeQueryTab = (id:string) => requestCloseTab(id)

function exportCSV(){ try{ if(!result.value || result.value.type!=='table') return; const cols = result.value.columns||[]; const rows = result.value.data||[]; const esc=(s:any)=>`"${String(s??'').replace(/"/g,'""')}"`; const lines = [cols.map(esc).join(',')].concat(rows.map((r:any)=> cols.map(c=>esc(r?.[c])).join(','))); const blob = new Blob([lines.join('\r\n')], { type: 'text/csv;charset=utf-8;' }); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='query.csv'; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href), 2000) } catch{} }
function exportExcel(){ try{ if(!result.value || result.value.type!=='table') return; const cols = result.value.columns||[]; const rows = result.value.data||[]; const html = `<table>${['<tr>'+cols.map(c=>`<th>${c}</th>`).join('')+'</tr>'].concat(rows.map((r:any)=>'<tr>'+cols.map(c=>`<td>${r?.[c]??''}</td>`).join('')+'</tr>')).join('')}</table>`; const blob = new Blob([`\ufeff${html}`], { type: 'application/vnd.ms-excel' }); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='query.xls'; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href), 2000) } catch{} }

onMounted(async()=>{ await loadConnections(); await loadConnInfo(); if (instances.value.length && connId.value) { expandConn[connId.value]=true; await loadDatabasesByConn(connId.value) } })
// ====== 挂载 CodeMirror，高亮与联想 ======
onMounted(()=>{
  const host = editorRef.value
  if (!host) return
  try {
    const keywordList = ['SELECT','FROM','WHERE','GROUP BY','ORDER BY','LIMIT','OFFSET','JOIN','LEFT JOIN','RIGHT JOIN','INNER JOIN','OUTER JOIN','ON','AND','OR','NOT','IN','IS NULL','IS NOT NULL','LIKE','BETWEEN','INSERT','INTO','VALUES','UPDATE','SET','DELETE','CREATE','TABLE','VIEW','INDEX','DROP','ALTER','ADD','PRIMARY KEY']
      .map(l=>({ label:l, type:'keyword', apply:l }))
    const columnsCache = new Map<string,string[]>()
    const columnsPending = new Set<string>()
    const getColKey = (db:string, table:string)=>`${db}.${table}`

    async function fetchTables(db:string): Promise<string[]> {
      try {
        // 先用新接口
        try {
          const { data } = await api.get(`/connections/${connId.value}/databases/${encodeURIComponent(db)}/tables`)
          if (Array.isArray(data)) return data
        } catch {}
        // 回退旧接口
        const { data } = await api.get('/ticket/tables', { params: { connId: connId.value, db, database: db, schema: db } })
        return Array.isArray(data)?data:[]
      } catch { return [] }
    }
    async function fetchColumns(db:string, table:string): Promise<string[]> {
      try {
        const key = getColKey(db, table)
        const cached = columnsCache.get(key); if (cached && cached.length) return cached
        if (columnsPending.has(key)) return []
        columnsPending.add(key)
        // 仅回退接口（与你后端兼容）
        const params = new URLSearchParams({ connId: String(connId.value||''), db, database: db, schema: db, table, tableName: table, tbl: table, format:'json' })
        let res = await fetch(`/api/ticket/columns?${params.toString()}`, { headers: { 'Accept': 'application/json' } })
        let data: any
        if (res.ok && String(res.headers.get('content-type')||'').includes('application/json')) data = await res.json()
        else {
          // 尝试文本 JSON
          const txt = await res.text(); if (txt && (txt.trim().startsWith('[')||txt.trim().startsWith('{'))) data = JSON.parse(txt)
        }
        let cols: string[] = []
        if (Array.isArray(data)) {
          if (data.length && typeof data[0]==='string') cols = data
          else {
            const keys=['name','column','column_name','COLUMN_NAME','field','Field']
            cols = (data as any[]).map(o=>{ for (const k of keys) if (o && typeof o[k]==='string') return o[k]; return '' }).filter(Boolean)
          }
        } else if (Array.isArray(data?.columns)) {
          const arr = data.columns; const keys=['name','column','column_name','COLUMN_NAME','field','Field']
          cols = (arr as any[]).map(o=>{ if (typeof o==='string') return o; for (const k of keys) if (o && typeof o[k]==='string') return o[k]; return '' }).filter(Boolean)
        }
        const uniq = Array.from(new Set(cols))
        columnsCache.set(key, uniq)
        columnsPending.delete(key)
        return uniq
      } catch { columnsPending.delete(`${db}.${table}`); return [] }
    }

    function buildDbList(): string[] { try { return dbsByConn[connId.value as any] || [] } catch { return [] } }
    function buildAliasMap(state: EditorState): Record<string,{db:string, table:string}> {
      const text = state.doc.toString()
      const alias: Record<string,{db:string, table:string}> = {}
      const reDbTable = /(from|join)\s+([a-zA-Z0-9_`]+)\s*\.\s*([a-zA-Z0-9_`]+)\s+(?:as\s+)?([a-zA-Z0-9_`]+)/gi
      const reTable = /(from|join)\s+([a-zA-Z0-9_`]+)\s+(?:as\s+)?([a-zA-Z0-9_`]+)/gi
      let m: RegExpExecArray | null
      while ((m = reDbTable.exec(text))) { const db=m[2].replace(/`/g,''); const table=m[3].replace(/`/g,''); const a=m[4].replace(/`/g,'').toLowerCase(); alias[a]={db,table} }
      while ((m = reTable.exec(text))) { const table=m[2].replace(/`/g,''); const a=m[3].replace(/`/g,'').toLowerCase(); if (!alias[a]) alias[a] = { db: currentDb.value || '', table } }
      return alias
    }
    const dynamicSQLCompletion = (context: CompletionContext) => {
      // 使用 matchBefore 精准判断"以点结尾"的场景，稳定触发补全
      const amap = buildAliasMap(context.state)
      const dbs = buildDbList()

      // db.table.
      const dbTableDot = context.matchBefore(/[A-Za-z0-9_`]+\.[A-Za-z0-9_`]+\.$/)
      if (dbTableDot) {
        const txt = dbTableDot.text
        try { console.debug('[cm.complete] db.table. hit:', txt) } catch {}
        const [dbRaw, tableRaw] = txt.slice(0, -1).split('.')
        const db = dbRaw.replace(/`/g,'')
        const table = tableRaw.replace(/`/g,'')
        return fetchColumns(db, table).then(cols=>{
          try { console.debug('[cm.complete] db.table. columns:', cols) } catch {}
          // 光标位于最后一个点之后，from 取当前位置，避免把 "db.table." 也纳入过滤前缀
          return { from: context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$]*$/ }
        }) as any
      }
      // alias. 或 表名.
      const aliasDot = context.matchBefore(/[A-Za-z0-9_`]+\.$/)
      if (aliasDot) {
        const token = aliasDot.text.replace('.', '').replace(/`/g,'')
        const hitAlias = amap[token.toLowerCase()]
        if (hitAlias) return fetchColumns(hitAlias.db||currentDb.value||'', hitAlias.table).then(cols=>{ try { console.debug('[cm.complete] alias columns:', cols) } catch {}; return { from: context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$]*$/ } }) as any
        if (currentDb.value) {
          const known = tablesByKey[`${connId.value}::${currentDb.value}`] || []
          if (known.includes(token)) {
            return fetchColumns(currentDb.value, token).then(cols=>{ try { console.debug('[cm.complete] table columns:', cols) } catch {}; return { from: context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$]*$/ } }) as any
          }
        }
        // 若是库. 则在下个分支处理
      }
      // db. → 表补全（即使本地列表未加载到该库名，也尝试请求）
      const dbDot = context.matchBefore(/[A-Za-z0-9_`]+\.$/)
      if (dbDot) {
        const dbName = dbDot.text.replace('.', '').replace(/`/g,'')
        try { console.debug('[cm.complete] db. hit:', dbName) } catch {}
        return fetchTables(dbName).then(list=>{ try { console.debug('[cm.complete] db. tables:', list) } catch {}; return { from: context.pos, options: (list||[]).map(t=>({label:t,type:'table'})), validFor:/[\w$]*$/ } }) as any
      }

      // 默认：通用词法 + 关键字/库/表列表
      const before = context.matchBefore(/[\w$\.\uFF0E\u3002]+$/)
      const word = (before?.text||'').trim()
      const items:any[] = []
      const parts = word.split('.')
      const pushAll = (arr:string[], type:string)=> arr.forEach(n=> items.push({label:n,type}))
      if (parts.length === 1) { items.push(...keywordList); pushAll(dbs, 'database'); if (currentDb.value) pushAll(tablesByKey[`${connId.value}::${currentDb.value}`]||[], 'table') }
      else if (parts.length === 2) {
        const [dbOrTable, maybeTable] = parts
        const dbHit = dbs.find(d=> String(d).toLowerCase()===dbOrTable.toLowerCase())
        if (dbHit && !maybeTable) return fetchTables(dbHit).then(list=>({ from: before ? before.from : context.pos, options: list.map(t=>({label:t,type:'table'})), validFor:/[\w$.]*$/ })) as any
        const hit = amap[dbOrTable.toLowerCase()]
        if (hit) return fetchColumns(hit.db||currentDb.value||'', hit.table).then(cols=>({ from: before ? before.from : context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$.]*$/ })) as any
        if (currentDb.value) return fetchColumns(currentDb.value, dbOrTable).then(cols=>({ from: before ? before.from : context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$.]*$/ })) as any
      } else if (parts.length >= 3) {
        const db = parts[0], table = parts[1]
        return fetchColumns(db, table).then(cols=>({ from: before ? before.from : context.pos, options: cols.map(c=>({label:c,type:'property'})), validFor:/[\w$.]*$/ })) as any
      }
      if (!items.length) items.push(...keywordList)
      try { console.debug('[cm.complete] default items:', items.slice(0,5)) } catch {}
      // 保持 CodeMirror 自身面板为主，不在此处弹自绘列表
      return { from: before ? before.from : context.pos, options: items, validFor:/[\w$\.\uFF0E\u3002]*$/ }
    }

    const state = EditorState.create({
      doc: '',
      extensions: [
        lineNumbers(),
        sql({ dialect: MySQL }),
        highlightActiveLine(),
        syntaxHighlighting(defaultHighlightStyle),
        keymap.of([
          ...completionKeymap,
          { key: 'Ctrl-Space', run: startCompletion }
        ]),
        autocompletion({ override:[dynamicSQLCompletion], icons:false, defaultKeymap:true, activateOnTyping:true }),
        EditorView.updateListener.of((v:any)=>{
          if (v.docChanged) {
            try {
              const txt = v.state.doc.toString();
              (globalThis as any).__next_sql_text = txt;
              updateActiveTabText(txt)
            } catch {}
            // 在输入 '.' 后，主动触发一次补全（db. / t. / db.table.）
            try {
              const head = v.state.selection.main.head
              const prev = v.state.doc.sliceString(Math.max(0, head - 1), head)
              if (prev === '.') startCompletion(v.view)
            } catch {}
          }
          syncEditorScrollerOverflow()
        }),
        EditorView.theme({
          '&':{ height:'100%' },
          '.cm-scroller':{ overflow:'auto' },
          '.cm-gutters':{ borderRight:'1px solid #e5e7eb', background:'#f8fafc', color:'#94a3b8' },
          '.cm-gutterElement':{ padding:'0 8px', fontSize:'12px' },
          '.cm-content':{
            fontFamily:'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
            fontSize:'13px',
            lineHeight:'1.6',
            whiteSpace:'pre'
          }
        })
      ]
    })
    cmView = new EditorView({ state, parent: host })
    // 初始标签
    if (!tabs.length) newTab()
    ensureActionBarVisible()
    try { cmView.focus() } catch {}
    // 监听容器尺寸变化，实时更新是否需要横向滚动
    try {
      if (editorResizeObserver) editorResizeObserver.disconnect()
      editorResizeObserver = new ResizeObserver(()=> syncEditorScrollerOverflow())
      if (editorWrapRef.value) editorResizeObserver.observe(editorWrapRef.value)
    } catch {}
    syncEditorScrollerOverflow()
  } catch {}
})

onUpdated(() => {
  setupToolbarObserver()
  ensureActionBarVisible()
  syncEditorScrollerOverflow()
})
</script>

<style scoped>
.sql-next { height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
.hdr { display:flex; align-items:center; gap:10px; padding:10px 12px; background: linear-gradient(90deg,#e8f0fe,#dbe8ff); border-bottom:1px solid #c7d2fe; color:#0b57d0; }
.hdr .title{ font-weight:700; }
.layout { flex:1 1 auto; min-height:0; display:grid; grid-template-columns: var(--left-w,270px) 6px 1fr; overflow:hidden; width:100%; }
.left { background:#f8fafc; border-right:1px solid #e5e7eb; display:flex; flex-direction:column; min-width:0; overflow:hidden; }
.tree { flex:1 1 auto; min-height:0; overflow-y:auto !important; overflow-x:hidden; padding:6px; }
.left, .tree, .dbs, .tbls, .inst-hd, .db-hd { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif; font-size: var(--dv-font-ui, 14px); }
.tree { scrollbar-width: thin; }
.tree::-webkit-scrollbar{ width: 10px; height: 10px; }
.tree::-webkit-scrollbar-thumb{ background:#94a3b8; border-radius:6px; }
.tree::-webkit-scrollbar-track{ background:transparent; }
.inst-hd,.db-hd { display:flex; align-items:center; gap:6px; padding:4px 6px; border-radius:6px; cursor:pointer; position:relative; }
.inst-hd:hover,.db-hd:hover{ background:#eef2ff; }
.arrow{ display:inline-block; width:10px; color:#64748b; }
.arrow.open{ transform:rotate(90deg); }
.mini{ display:inline-flex; align-items:center; justify-content:center; width:18px; height:18px; border:1px solid #cbd5e1; border-radius:4px; background:#fff; color:#334155; position:absolute; right:6px; top:4px; }
.mini.filter.active{ background:#e6f0ff; border-color:#93c5fd; color:#0b57d0; }
/* 库级过滤输入：与库名同一行，显示在库名右侧，不覆盖库名 */
.db-filter-input{ position:static; margin-left:6px; height:22px; border:1px solid #cbd5e1; border-radius:4px; padding:0 6px; font-size:12px; min-width:140px; }
.dbs, .tbls{ list-style:none; margin:0; padding:0 0 0 16px; }
.tbl{ padding:2px 6px; border-radius:4px; cursor:pointer; }
.tbl:hover{ background:#f1f5f9; }
.muted{ color:#9ca3af; padding:6px; }
.panel{ position:absolute; top:0; z-index:1000; border:1px solid #e5e7eb; border-radius:8px; background:#fff; box-shadow:0 8px 16px rgba(0,0,0,.08); }
.inst-panel{ position: fixed; width: 320px; max-height: 360px; overflow:auto; }
.inst-panel .ph-search{ padding:6px 10px; border-bottom:1px solid #e5e7eb; background:#fff; position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; }
.inst-panel .ph-search{ position: sticky; top:0; position: relative; }
.inst-panel .ph-search .ico{ position:absolute; left:18px; top:50%; transform:translateY(-50%); color:#94a3b8; font-size:14px; pointer-events:none; }
.inst-panel .ph-search input{ width:100%; height:26px; border:1px solid #c7d2fe; border-radius:6px; padding:2px 34px 2px 32px; font-size:13px; outline:none; }
.inst-panel .ph-search input:focus{ border-color:#c7d2fe; box-shadow:none; }
.inst-panel .ph-search .clear{ position:absolute; right:18px; top:50%; transform:translateY(-50%); width:24px; height:24px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; display:inline-flex; align-items:center; justify-content:center; }
.panel .phd{ display:flex; align-items:center; justify-content:space-between; padding:6px 8px; border-bottom:1px solid #e5e7eb; color:#0b57d0; font-weight:600; }
.panel .plist{ max-height:220px; overflow:auto; padding:6px 8px; }
.panel .opt{ display:block; padding:4px 6px; }
.gsearch{ border-top:1px solid #e5e7eb; padding:8px; flex:0 0 auto; }
.gsearch .searchbox{ position: relative; }
.gsearch .searchbox .ico{ position:absolute; left:8px; top:50%; transform:translateY(-50%); color:#94a3b8; font-size:14px; }
.gsearch .searchbox input{ width:100%; height:28px; padding:4px 64px 4px 28px; border:1px solid #c7d2fe; border-radius:6px; outline:none; }
.gsearch .searchbox input:focus{ border-color:#c7d2fe; box-shadow:none; }
.gsearch .searchbox .action{ position:absolute; top:50%; transform:translateY(-50%); right:8px; width:24px; height:24px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; cursor:pointer; margin-left:4px; }
.gsearch .searchbox .action + .action{ right:36px; }
.vsplit{ background:transparent; position:relative; cursor:col-resize; }
.vsplit::before{ content:""; position:absolute; left:2px; top:0; bottom:0; width:2px; background:#e5e7eb; }
.vsplit:hover::before{ background:#cbd5e1; }
.right{ position:relative; display:flex; flex-direction:column; min-height:0; min-width:0; z-index: 0; background:#f8fafc; }
.right > .editor-wrap{ margin-top:0; }
.toolbar{ display:none; }
.tabs{ margin:6px 12px 0 12px; min-width:0; overflow:hidden; position: sticky; top: 0; z-index: 10000; background: #f8fafc; border-bottom:1px solid #e5e7eb; min-height: 40px; }
.hdr-actions{ display:flex; gap:8px; align-items:center; margin-left:auto; }
.hdr-actions.sticky{ display:flex !important; visibility:visible !important; opacity:1 !important; pointer-events:auto !important; }
.hdr-actions .icon-btn{ width:32px; height:32px; border-radius:6px; border:1px solid #c9c9c9; background:#fff; color:#333; }
.hdr-actions .icon-btn.add{ background:#e8f0fe; border-color:#3b82f6; color:#0b57d0; }
.hdr-actions .icon-btn.warn{ background:#fff; border-color:#ef4444; color:#b91c1c; }
.hdr-actions .icon-btn.info{ background:#e8f0fe; border-color:#3b82f6; color:#0b57d0; }
.hdr-actions .icon-btn svg{ width:18px; height:18px; }
.tabs :deep(.tq-tabbar){ flex-wrap:nowrap; margin-bottom:0; height: 36px; align-items: flex-end; }
.hdr-actions{ display:flex; gap:8px; align-items:center; margin-left:auto; }
.hdr-actions.sticky{ display:flex !important; visibility:visible !important; opacity:1 !important; pointer-events:auto !important; }
.hdr-actions .icon-btn{ width:32px; height:32px; border-radius:6px; border:1px solid #d1d5db; background:#fff; color:#374151; box-shadow:none; transition: background-color .15s ease, box-shadow .15s ease, transform .06s ease; }
.hdr-actions .icon-btn.add{ background:#0b57d0; border-color:#0b57d0; color:#fff; }
.hdr-actions .icon-btn.warn{ background:#fff1f2; border-color:#fecaca; color:#b91c1c; }
.hdr-actions .icon-btn.info{ background:#e6f0ff; border-color:#c7d2fe; color:#0b57d0; }
.hdr-actions .icon-btn:hover{ background:#f5f7ff; box-shadow: 0 0 0 2px rgba(59,130,246,.25); }
/* 执行按钮在悬浮时保持蓝底并略微加深，不被通用 hover 覆盖 */
.hdr-actions .icon-btn.add:hover{ background:#0a49b7; border-color:#0a49b7; color:#fff; box-shadow: 0 0 0 2px rgba(59,130,246,.28); }
/* 停止与信息按钮的悬浮更明显一些 */
.hdr-actions .icon-btn.warn:hover{ background:#fecaca; box-shadow: 0 0 0 2px rgba(239,68,68,.25); }
.hdr-actions .icon-btn.info:hover{ background:#dbe8ff; box-shadow: 0 0 0 2px rgba(59,130,246,.22); }
.hdr-actions .icon-btn:active{ transform: translateY(1px); }
.hdr-actions .icon-btn:focus-visible{ outline: 2px solid #93c5fd; outline-offset: 2px; }
.hdr-actions .icon-btn svg{ width:16px; height:16px; }
.hdr-actions .icon-btn:disabled{ opacity:.6; cursor:not-allowed; box-shadow:none; }
.toolbar-actions .icon-btn{ width:32px; height:32px; border-radius:10px; }
.toolbar-actions .icon-btn svg{ width:18px; height:18px; }
.toolbar .tab, .tabs .tab{ display:flex; align-items:center; gap:6px; padding:6px 12px; background:#f7f9fc; border:1px solid #e5e7eb; border-bottom-color:#e5e7eb; border-radius:10px 10px 0 0; cursor:pointer; color:#374151; font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "PingFang SC", "Microsoft YaHei", sans-serif; font-size: var(--dv-font-ui, 14px); box-shadow: 0 1px 2px rgba(0,0,0,.04); }
.toolbar .tab.active, .tabs .tab.active{ background:#fff; border-color:#99b7ff; border-bottom-color:#99b7ff; box-shadow: 0 0 0 2px rgba(59,130,246,.25); }
.toolbar .tab .close{ border:none; background:transparent; cursor:pointer; color:#64748b; }
.toolbar .add{ margin-left:6px; width:28px; height:28px; border:1px solid #e5e7eb; background:#fff; border-radius:8px; cursor:pointer; }
.editor-wrap{ position:relative; overflow: visible; flex: 0 0 auto; width:100%; z-index:1; }
.editor{ height:150px; min-height:100px; overflow:hidden; position:relative; }
.tabs + .editor-wrap { margin-top: 0; }
.editor :deep(.cm-editor){ height:100% !important; max-width:100%; position: relative; z-index: 1; }
.editor :deep(.cm-scroller){ height:100%; overflow:auto; scrollbar-width: thin; padding-right:0; padding-bottom:0; max-width:100%; width: 100%; }
.editor :deep(.cm-content){
  white-space: pre;
  /* 仅在内容超出时触发横向滚动：不再强制比容器更宽 */
  min-width: 100%;
}
.editor :deep(.cm-tooltip){ z-index: 30000; position: absolute; }
.editor :deep(.cm-tooltip-autocomplete){ z-index: 30010; }
.editor :deep(.cm-content) { caret-color: #111827; }
.editor :deep(.cm-cursor) { border-left-color: #111827 !important; }
.editor :deep(.cm-scroller::-webkit-scrollbar){ width:10px; height:10px; }
.editor :deep(.cm-scroller::-webkit-scrollbar-thumb){ background:#94a3b8; border-radius:6px; }
.editor :deep(.cm-scroller::-webkit-scrollbar-thumb:hover){ background:#64748b; }
.editor :deep(.cm-scroller::-webkit-scrollbar-track){ background:transparent; }
.hsplit{ height:16px; cursor:row-resize; position:relative; background:transparent; }
.hsplit::before{ content:""; position:absolute; left:0; right:0; top:5px; height:2px; background:#cfd3dc; }
.fab-actions{ position:absolute; right:12px; top:6px; display:flex; gap:8px; z-index:30; pointer-events:auto; background:#f1f5f9; padding:4px 6px; border-radius:8px; box-shadow:0 6px 16px rgba(15,23,42,0.12); }
.code{ width:100%; height:100%; padding:10px; border:1px solid #e5e7eb; border-radius:8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size:13px; line-height:1.6; outline:none; overflow:auto; white-space: pre-wrap; }
.result{ display:flex; flex-direction:column; min-height:0; position:relative; z-index:1; background:#f8fafc; }
.rhdr{ padding:8px 12px; background:#f8fafc; border-bottom:1px solid #e5e7eb; }
.rbody{ flex:1 1 auto; min-height:0; overflow:auto; padding:12px; scrollbar-width: thin; scrollbar-color:#94a3b8 transparent; background:#f8fafc; position:relative; }
.rbody.table-mode{ padding:0; }
.rbody.table-mode .table-holder{ height:100%; display:flex; flex-direction:column; }
.rbody.table-mode :deep(.tq-table-fixed){ flex:1 1 auto; min-height:0; }
.rbody.table-mode :deep(.tq-scroll-x){ z-index: 2; }
.rbody::-webkit-scrollbar{ width:10px; height:10px }
.rbody::-webkit-scrollbar-thumb{ background:#94a3b8; border-radius:6px }
.rbody::-webkit-scrollbar-thumb:hover{ background:#64748b }
.table-scroll{ overflow-y:auto; overflow-x:clip !important; -ms-overflow-style: none; scrollbar-width: none; }
.x-scroll{ flex:0 0 auto; height:16px; min-height:16px; overflow-x:auto; overflow-y:hidden; border-top:1px solid #e5e7eb; background:#f8fafc; }
.x-scroll{ display: var(--xscroll-visible, block); }
.x-scroll .spacer{ height:1px; }
.x-scroll{ scrollbar-width: thin; scrollbar-color:#94a3b8 transparent; }
.x-scroll::-webkit-scrollbar{ height:10px; }
.x-scroll::-webkit-scrollbar-track{ background:transparent; }
.x-scroll::-webkit-scrollbar-thumb{ background:#94a3b8; border-radius:6px; }
.x-scroll:hover::-webkit-scrollbar-thumb{ background:#64748b; }
.tq-pagination{ flex:0 0 auto; display:flex; align-items:center; gap:12px; padding:8px 12px; border-top:1px solid #e5e7eb; background:#fff; color:#374151; }
.tq-pagination .muted{ color:#64748b; }
.tq-pagination .icon-btn{ width:28px; height:28px; border:1px solid #e5e7eb; border-radius:10px; background:#fff; color:#0b57d0; cursor:pointer; }
.tq-pagination .icon-btn:hover{ background:#f8fafc; }
.tq-pagination input[type="number"]{ height:28px; line-height:28px; border:1px solid #e5e7eb; border-radius:8px; padding:2px 8px; box-sizing:border-box; color:#111827; }
.tq-pagination select{ height:28px; border:1px solid #e5e7eb; border-radius:8px; padding:2px 28px 2px 8px; color:#111827; }
/* 结果区占位提示：字体更小、更淡，便于与编辑区区分 */
.rbody .placeholder{ font-size: 13px; color:#9aa3b2; text-align:center; padding: 36px 8px; }
/* 浮动库过滤输入框样式 */
.db-filter-float{ position: fixed; z-index: 12000; height: 28px; padding: 4px 8px; border:1px solid #93c5fd; border-radius:6px; background:#fff; color:#0b57d0; box-shadow:0 8px 24px rgba(0,0,0,.15); width: 220px; outline:none; }
.db-filter-float:focus{ border-color:#93c5fd; box-shadow:0 0 0 2px rgba(147,197,253,.35); }
/* 移除自绘补全面板样式，使用 CodeMirror 自带面板 */
</style>

