<template>
  <div class="sql-console-page">
    <!-- 页面头部 -->
    <header class="console-header">
      <div class="header-left">
        <h1 class="page-title">SQL控制台</h1>
        <span class="conn-info" v-if="connInfo">[{{ connInfo }}]</span>
      </div>
      <div class="header-right">
        <button class="btn-close" @click="closePage" title="关闭">×</button>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <div class="console-content" :style="{ '--left-width': leftCollapsed ? '0px' : '230px' }">
      <!-- 左侧数据库树 -->
      <div class="console-left" :class="{ collapsed: leftCollapsed }">
        <div class="left-tools">
          <button class="db-toggle" :class="{ show: dbDropdownOpen }" @click="dbDropdownOpen = !dbDropdownOpen">
            数据库 {{ selectedDbs.length > 0 ? `(${selectedDbs.length})` : '' }}
          </button>
        </div>
        
        <!-- 数据库树结构 -->
        <div class="db-tree" v-if="databases.length > 0">
          <div v-for="db in filteredDatabases" :key="db" class="db-item">
            <div class="db-header" @click="toggleDbExpand(db)">
              <span class="expand-icon" :class="{ expanded: expandedDb[db] }">▶</span>
              <span class="db-name">{{ db }}</span>
            </div>
            <div v-if="expandedDb[db]" class="table-list">
              <div v-if="tablesLoading[db]" class="loading">加载中...</div>
              <div v-else-if="filteredTables(db).length === 0" class="no-tables">暂无表</div>
              <div v-else>
                <div v-for="table in filteredTables(db)" :key="table" 
                     class="table-item" @click="appendTableToSQL(db, table)">
                  {{ table }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧编辑器和结果区 -->
      <div class="console-right">
        <!-- SQL编辑器 -->
        <div class="sql-editor" ref="editorRef">
          <div class="editor-toolbar">
            <button class="btn-execute" @click="executeSQL" :disabled="running">
              {{ running ? '执行中...' : '执行' }}
            </button>
            <button class="btn-stop" @click="stopExecution" :disabled="!running">停止</button>
            <button class="btn-plan" @click="viewPlan">执行计划</button>
            <button class="btn-beautify" @click="beautifySQL">格式化</button>
          </div>
          <div class="editor-content" ref="codeRef"></div>
        </div>

        <!-- 查询结果 -->
        <div class="query-result">
          <div class="result-header">
            <span>查询结果</span>
          </div>
          <div class="result-content">
            <template v-if="result && result.type === 'table'">
              <div class="table-result">
                <!-- 这里复用原有的表格组件逻辑 -->
                <div v-if="result.data && result.data.length > 0">
                  <table class="result-table">
                    <thead>
                      <tr>
                        <th v-for="col in result.columns" :key="col">{{ col }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, idx) in result.data" :key="idx">
                        <td v-for="col in result.columns" :key="col">{{ row[col] }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </template>
            <template v-else-if="result && result.type === 'text'">
              <pre class="text-result">{{ result.text }}</pre>
            </template>
            <template v-else>
              <div class="empty-result">在此显示查询结果或执行信息</div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import api from '../../api'

// 从URL参数获取连接ID
const urlParams = new URLSearchParams(window.location.search)
const connId = urlParams.get('connId')

// 响应式数据
const connInfo = ref('')
const leftCollapsed = ref(false)
const dbDropdownOpen = ref(false)
const selectedDbs = ref([])
const databases = ref([])
const tables = reactive({})
const tablesLoading = reactive({})
const expandedDb = reactive({})
const sql = ref('')
const result = ref(null)
const running = ref(false)

// 编辑器相关
const editorRef = ref(null)
const codeRef = ref(null)
let editorView = null

// 计算属性
const filteredDatabases = computed(() => {
  return databases.value || []
})

// 方法
function closePage() {
  window.close()
}

function toggleDbExpand(db) {
  expandedDb[db] = !expandedDb[db]
  if (expandedDb[db] && !tables[db]) {
    loadTables(db)
  }
}

function filteredTables(db) {
  return tables[db] || []
}

async function loadTables(db) {
  if (!db || !connId) return
  tablesLoading[db] = true
  try {
    const params = { connId, db, database: db }
    const { data } = await api.get('/ticket/tables', { params })
    tables[db] = Array.isArray(data) ? data : []
  } catch (e) {
    console.error(`加载 ${db} 表失败`, e)
  } finally {
    tablesLoading[db] = false
  }
}

function appendTableToSQL(db, table) {
  const snippet = `-- ${db}.${table}\nSELECT * FROM ${db}.${table} LIMIT 100;\n`
  const prefix = sql.value && !/\n$/.test(sql.value) ? '\n' : ''
  sql.value += prefix + snippet
  
  // 如果有编辑器实例，同步更新
  if (editorView) {
    try {
      const doc = editorView.state.doc.toString()
      const insertPrefix = doc && !/\n$/.test(doc) ? '\n' : ''
      const insert = insertPrefix + snippet
      editorView.dispatch({
        changes: { from: editorView.state.doc.length, to: editorView.state.doc.length, insert }
      })
      editorView.focus()
    } catch (e) {
      console.error('编辑器更新失败', e)
    }
  }
}

async function executeSQL() {
  if (!sql.value.trim()) return
  running.value = true
  result.value = { type: 'text', text: '执行中...' }
  
  try {
    const { data } = await api.post('/ticket/execute', {
      connId: connId,
      sql: sql.value,
      page: 1,
      pageSize: 100
    })
    
    if (data && Array.isArray(data.data) && data.columns) {
      result.value = {
        type: 'table',
        data: data.data,
        columns: data.columns,
        total: data.total || data.data.length
      }
    } else if (typeof data === 'string') {
      result.value = { type: 'text', text: data }
    } else if (data && data.message) {
      result.value = { type: 'text', text: data.message }
    } else {
      result.value = { type: 'text', text: '执行完成' }
    }
  } catch (e) {
    const msg = e?.response?.data?.detail || e?.message || '执行失败'
    result.value = { type: 'text', text: String(msg) }
  } finally {
    running.value = false
  }
}

function stopExecution() {
  running.value = false
}

async function viewPlan() {
  if (!sql.value.trim()) return
  try {
    const { data } = await api.post('/ticket/plan', {
      connId: connId,
      sql: sql.value
    })
    
    if (typeof data === 'string') {
      result.value = { type: 'text', text: data }
    } else if (data && data.message) {
      result.value = { type: 'text', text: data.message }
    } else {
      result.value = { type: 'text', text: JSON.stringify(data, null, 2) }
    }
  } catch (e) {
    result.value = { type: 'text', text: e?.response?.data?.detail || e.message || '获取执行计划失败' }
  }
}

function beautifySQL() {
  if (!sql.value) return
  let s = sql.value
  s = s.replace(/[\t ]+/g, ' ').replace(/\s*;\s*/g, ';\n').replace(/\n{3,}/g, '\n\n').trim() + '\n'
  sql.value = s
  
  // 同步到编辑器
  if (editorView) {
    try {
      const len = editorView.state.doc.length
      editorView.dispatch({
        changes: { from: 0, to: len, insert: s }
      })
    } catch (e) {
      console.error('编辑器同步失败', e)
    }
  }
}

// 初始化
async function init() {
  if (!connId) {
    console.error('缺少连接ID参数')
    return
  }
  
  try {
    // 获取连接信息
    const { data: conn } = await api.get(`/connections/${connId}`)
    // 使用与原浮动窗口相同的显示逻辑：优先显示description，然后是user@ip:port
    const displayName = conn.description || `${conn.ip}:${conn.port}` || `#${conn.id}`
    connInfo.value = `${conn.user}@${conn.ip}:${conn.port} (${displayName})`
    
    // 加载数据库列表
    const { data: dbs } = await api.get('/ticket/databases', {
      params: { connId }
    })
    databases.value = Array.isArray(dbs) ? dbs : []
  } catch (e) {
    console.error('初始化失败', e)
  }
}

onMounted(() => {
  init()
})
</script>

<style scoped>
.sql-console-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: system-ui, -apple-system, sans-serif;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(90deg, #e8f0fe 0%, #dbe8ff 100%);
  border-bottom: 1px solid #c7d2fe;
  color: #0b57d0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
}

.conn-info {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #0b57d0;
  font-size: 20px;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  background: #eef2ff;
  color: #063e99;
}

.console-content {
  flex: 1;
  display: grid;
  grid-template-columns: var(--left-width) 1fr;
  overflow: hidden;
}

.console-left {
  background: #f8fafc;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.console-left.collapsed {
  display: none;
}

.left-tools {
  padding: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.db-toggle {
  height: 28px;
  padding: 0 10px;
  border: 1px solid #c7d2fe;
  border-radius: 6px;
  background: #fff;
  color: #0b57d0;
  cursor: pointer;
  font-size: 14px;
}

.db-toggle.show {
  background: #e8f0fe;
  border-color: #3b82f6;
}

.db-tree {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.db-item {
  margin-bottom: 4px;
}

.db-header {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.db-header:hover {
  background: #e5e7eb;
}

.expand-icon {
  width: 16px;
  font-size: 12px;
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.db-name {
  margin-left: 4px;
}

.table-list {
  margin-left: 20px;
  padding-left: 8px;
  border-left: 1px solid #e5e7eb;
}

.table-item {
  padding: 4px 8px;
  cursor: pointer;
  font-size: 13px;
  border-radius: 3px;
  color: #64748b;
}

.table-item:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.loading, .no-tables {
  padding: 4px 8px;
  font-size: 13px;
  color: #9ca3af;
}

.console-right {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sql-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid #e5e7eb;
}

.editor-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.editor-toolbar button {
  height: 32px;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #fff;
  color: #374151;
  cursor: pointer;
  font-size: 14px;
}

.editor-toolbar button:hover {
  background: #f9fafb;
}

.editor-toolbar button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-execute {
  background: #0b57d0 !important;
  color: #fff !important;
  border-color: #0b57d0 !important;
}

.btn-execute:hover:not(:disabled) {
  background: #063e99 !important;
}

.editor-content {
  flex: 1;
  min-height: 200px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  padding: 12px;
  background: #fff;
  border: none;
  outline: none;
  resize: none;
  overflow: auto;
}

.query-result {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.result-header {
  padding: 8px 12px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 500;
  color: #374151;
}

.result-content {
  flex: 1;
  overflow: auto;
  padding: 12px;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.result-table th,
.result-table td {
  padding: 8px 12px;
  text-align: left;
  border: 1px solid #e5e7eb;
}

.result-table th {
  background: #f8fafc;
  font-weight: 500;
  color: #374151;
}

.result-table td {
  color: #111827;
}

.text-result {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  color: #111827;
  white-space: pre-wrap;
  margin: 0;
}

.empty-result {
  color: #9ca3af;
  font-style: italic;
  text-align: center;
  padding: 40px;
}
</style>
