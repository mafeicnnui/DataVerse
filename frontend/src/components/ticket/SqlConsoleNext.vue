<template>
  <div class="sql-next">
    <header class="hdr">
      <div class="title">SQL控制台（Next）</div>
      <div class="conn" v-if="connInfo">[{{ connInfo }}]</div>
    </header>
    <div class="layout" :style="{ '--left-w': leftWidth + 'px' }">
      <!-- 左侧：三层树（实例->库->表） + 全局搜索 -->
      <aside class="left">
        <div class="tree" role="tree">
          <div class="inst" v-for="inst in instances" :key="'i-'+inst.id">
            <div class="inst-hd" @click="toggleConn(inst.id)" @mouseenter="hoverInst=inst.id" @mouseleave="hoverInst=''">
              <span class="arrow" :class="{open: expandConn[inst.id]}" aria-hidden="true">›</span>
              <span class="label" :title="inst.description || (inst.ip + ':' + inst.port) || ('#' + inst.id)">
                {{ inst.description || (inst.ip + ':' + inst.port) || ('#' + inst.id) }}
              </span>
              <button v-show="hoverInst===inst.id" class="mini filter" title="选择实例库" @click.stop="openInstFilter(inst)">⚙</button>
            </div>
            <!-- 实例库过滤面板（不遮挡菜单，显示在菜单右侧） -->
            <div v-if="instFilterVisible===inst.id" class="panel" :style="{ left: (leftWidth + 12) + 'px' }" @mousedown.stop>
              <div class="phd">选择需要显示的库<button class="x" @click="instFilterVisible=''">×</button></div>
              <div class="plist">
                <label class="opt" v-for="db in (dbsByConn[inst.id]||[])" :key="'p-'+inst.id+'-'+db">
                  <input type="checkbox" :checked="isDbSelected(inst.id, db)" @change="onDbSelect(inst.id, db, $event)">
                  <span>{{ db }}</span>
                </label>
              </div>
            </div>
            <ul v-show="expandConn[inst.id]" class="dbs">
              <li class="db" v-for="db in filteredDbList(inst.id)" :key="'db-'+inst.id+'-'+db">
                <div class="db-hd" @click="toggleDb(inst.id, db)" @mouseenter="hoverDb=inst.id+':'+db" @mouseleave="hoverDb=''">
                  <span class="arrow" :class="{open: !!expandDbByConn[inst.id]?.[db]}" aria-hidden="true">›</span>
                  <span class="label">{{ db }}</span>
                  <button v-show="hoverDb===inst.id+':'+db" class="mini filter" title="过滤该库的表" @click.stop="openDbFilter(inst.id, db)">🔍</button>
                </div>
                <ul v-show="expandDbByConn[inst.id]?.[db]" class="tbls">
                  <li class="tbl" v-for="t in filteredTablesFor(inst.id, db)" :key="'t-'+inst.id+'-'+db+'-'+t" @click="appendSnip(db, t)">{{ t }}</li>
                  <li class="muted" v-if="loadingKey(inst.id, db)">加载中...</li>
                  <li class="muted" v-else-if="emptyKey(inst.id, db)">无表</li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
        <div class="gsearch">
          <input v-model.trim="globalDbSearch" placeholder="全局库搜索（空格分隔，或关系）" />
        </div>
      </aside>
      <div class="vsplit" @mousedown="startDrag"></div>
      <!-- 右侧：编辑器在上，结果在下（保持与旧页一致的按钮组） -->
      <main class="right">
        <div class="toolbar">
          <button class="btn primary" @click="exec" :disabled="running">{{ running ? '执行中...' : '执行' }}</button>
          <button class="btn" @click="stop" :disabled="!running">停止</button>
          <button class="btn" @click="viewPlan">执行计划</button>
          <button class="btn" @click="beautify">格式化</button>
        </div>
        <div class="editor" ref="editorRef"><div ref="codeRef" class="code" contenteditable="true"></div></div>
        <div class="result">
          <div class="rhdr">查询结果</div>
          <div class="rbody">
            <div v-if="result && result.type==='table'">
              <table class="rtbl">
                <thead><tr><th v-for="c in result.columns" :key="c">{{ c }}</th></tr></thead>
                <tbody>
                  <tr v-for="(row, i) in result.data" :key="'r'+i">
                    <td v-for="c in result.columns" :key="c">{{ row[c] }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <pre v-else-if="result && result.type==='text'" class="txt">{{ result.text }}</pre>
            <div v-else class="muted">在此显示查询结果或执行信息</div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../../api'

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
const globalDbSearch = ref('')
const hoverInst = ref<string|number>('')
const hoverDb = ref<string>('')
const leftWidth = ref(270)

// 右侧
const codeRef = ref<HTMLElement|null>(null)
const editorRef = ref<HTMLElement|null>(null)
const running = ref(false)
const result = ref<any|null>(null)

function toggleConn(id:any){ expandConn[id] = !expandConn[id]; if (expandConn[id] && !dbsByConn[id]) loadDatabasesByConn(id) }
function toggleDb(id:any, db:string){ if (!expandDbByConn[id]) expandDbByConn[id] = {}; expandDbByConn[id][db] = !expandDbByConn[id][db]; if (expandDbByConn[id][db]) loadTablesByConnDb(id, db) }

function openInstFilter(inst:any){ instFilterVisible.value = inst.id; if (!dbsByConn[inst.id]) loadDatabasesByConn(inst.id); if (!selectedDbByConn[inst.id]) selectedDbByConn[inst.id] = new Set<string>() }
function isDbSelected(id:any, db:string){ return !!selectedDbByConn[id]?.has(db) }
function onDbSelect(id:any, db:string, ev:Event){ const on=(ev.target as HTMLInputElement).checked; if(!selectedDbByConn[id]) selectedDbByConn[id]=new Set<string>(); if(on) selectedDbByConn[id].add(db); else selectedDbByConn[id].delete(db) }
function filteredDbList(id:any){ const all = dbsByConn[id]||[]; const sel=selectedDbByConn[id]; const tokens=(globalDbSearch.value||'').trim().toLowerCase().split(/\s+/).filter(Boolean); return all.filter(db=>{ if(sel&&sel.size>0&&!sel.has(db)) return false; if(!tokens.length) return true; const s=db.toLowerCase(); return tokens.some(t=>s.includes(t)) }) }
function openDbFilter(id:any, db:string){ const q = prompt('过滤该库的表（空格分隔，或关系）','')||''; const toks=q.trim().toLowerCase().split(/\s+/).filter(Boolean); const key = `${id}::${db}`; const all = tablesByKey[key]||[]; if(!toks.length) return; tablesByKey[key] = all.filter(t=> toks.some(k=> t.toLowerCase().includes(k))) }
function filteredTablesFor(id:any, db:string){ const key=`${id}::${db}`; return tablesByKey[key]||[] }
function loadingKey(id:any, db:string){ return !!tablesLoading[`${id}::${db}`] }
function emptyKey(id:any, db:string){ const key=`${id}::${db}`; const arr=tablesByKey[key]; return Array.isArray(arr) && arr.length===0 }

async function loadConnections(){ try{ const {data}=await api.get('/connections'); instances.value=Array.isArray(data)?data:[] }catch{ instances.value=[] } }
async function loadConnInfo(){ try{ const {data}=await api.get(`/connections/${connId.value}`); connInfo.value = `${data.user}@${data.ip}:${data.port} (${data.description||data.ip+':'+data.port||('#'+data.id)})` }catch{ connInfo.value='' } }
async function loadDatabasesByConn(id:any){ try{ const {data}=await api.get(`/connections/${id}/databases`); dbsByConn[id]=Array.isArray(data)?data:[] }catch{ dbsByConn[id]=dbsByConn[id]||[] } }
async function loadTablesByConnDb(id:any, db:string){ const key=`${id}::${db}`; tablesLoading[key]=true; try{ const {data}=await api.get(`/connections/${id}/databases/${encodeURIComponent(db)}/tables`); tablesByKey[key]=Array.isArray(data)?data:[] }catch{ tablesByKey[key]=tablesByKey[key]||[] } finally{ tablesLoading[key]=false }
}

function startDrag(e:MouseEvent){ const sx=e.clientX, sw=leftWidth.value; const onMove=(ev:MouseEvent)=>{ leftWidth.value=Math.max(180, Math.min(560, sw + ev.clientX - sx)) }; const onUp=()=>{ window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp)}; window.addEventListener('mousemove', onMove); window.addEventListener('mouseup', onUp, {once:true}) }

function appendSnip(db:string, tbl:string){ const host=codeRef.value; if(!host) return; const prefix = host.textContent && !/\n$/.test(host.textContent||'') ? '\n' : ''; const snip = `-- ${db}.${tbl}\nSELECT * FROM ${db}.${tbl} LIMIT 100;\n`; host.textContent = (host.textContent||'') + prefix + snip }
async function exec(){ const sql=(codeRef.value?.textContent||'').trim(); if(!sql) return; running.value=true; result.value={ type:'text', text:'执行中...' }; try{ const {data}=await api.post('/ticket/execute',{ connId: connId.value, sql }); if (data && Array.isArray(data.data) && data.columns) { result.value={ type:'table', data:data.data, columns:data.columns } } else if (typeof data==='string') { result.value={ type:'text', text:data } } else { result.value={ type:'text', text: data?.message || '执行完成' } } }catch(e:any){ result.value={ type:'text', text: e?.response?.data?.detail || e?.message || '执行失败' } } finally{ running.value=false } }
function stop(){ running.value=false }
function viewPlan(){ /* 保留占位，与旧页一致 */ }
function beautify(){ const host=codeRef.value; if(!host) return; let s=host.textContent||''; s=s.replace(/[\t ]+/g,' ').replace(/\s*;\s*/g,';\n').replace(/\n{3,}/g,'\n\n').trim()+'\n'; host.textContent=s }

onMounted(async()=>{ await loadConnections(); await loadConnInfo(); if (instances.value.length && connId.value) { expandConn[connId.value]=true; await loadDatabasesByConn(connId.value) } })
</script>

<style scoped>
.sql-next { height: 100vh; display: flex; flex-direction: column; }
.hdr { display:flex; align-items:center; gap:10px; padding:10px 12px; background: linear-gradient(90deg,#e8f0fe,#dbe8ff); border-bottom:1px solid #c7d2fe; color:#0b57d0; }
.hdr .title{ font-weight:700; }
.layout { flex:1 1 auto; min-height:0; display:grid; grid-template-columns: var(--left-w,270px) 6px 1fr; }
.left { background:#f8fafc; border-right:1px solid #e5e7eb; display:flex; flex-direction:column; min-width:0; }
.tree { flex:1 1 auto; min-height:0; overflow:auto; padding:6px; }
.inst-hd,.db-hd { display:flex; align-items:center; gap:6px; padding:4px 6px; border-radius:6px; cursor:pointer; position:relative; }
.inst-hd:hover,.db-hd:hover{ background:#eef2ff; }
.arrow{ display:inline-block; width:10px; color:#64748b; }
.arrow.open{ transform:rotate(90deg); }
.mini{ display:inline-flex; align-items:center; justify-content:center; width:18px; height:18px; border:1px solid #cbd5e1; border-radius:4px; background:#fff; color:#334155; position:absolute; right:6px; top:4px; }
.dbs, .tbls{ list-style:none; margin:0; padding:0 0 0 16px; }
.tbl{ padding:2px 6px; border-radius:4px; cursor:pointer; }
.tbl:hover{ background:#f1f5f9; }
.muted{ color:#9ca3af; padding:6px; }
.panel{ position:absolute; top:0; z-index:1000; border:1px solid #e5e7eb; border-radius:8px; background:#fff; box-shadow:0 8px 16px rgba(0,0,0,.08); }
.panel .phd{ display:flex; align-items:center; justify-content:space-between; padding:6px 8px; border-bottom:1px solid #e5e7eb; color:#0b57d0; font-weight:600; }
.panel .plist{ max-height:220px; overflow:auto; padding:6px 8px; }
.panel .opt{ display:block; padding:4px 6px; }
.gsearch{ border-top:1px solid #e5e7eb; padding:8px; }
.gsearch input{ width:100%; height:28px; padding:4px 8px; border:1px solid #c7d2fe; border-radius:6px; }
.vsplit{ background:transparent; position:relative; cursor:col-resize; }
.vsplit::before{ content:""; position:absolute; left:2px; top:0; bottom:0; width:2px; background:#e5e7eb; }
.vsplit:hover::before{ background:#cbd5e1; }
.right{ display:grid; grid-template-rows: auto auto 1fr; min-height:0; }
.toolbar{ display:flex; gap:8px; align-items:center; padding:8px 12px; background:#f8fafc; border-bottom:1px solid #e5e7eb; }
.btn{ height:28px; padding:0 12px; border:1px solid #d1d5db; border-radius:6px; background:#fff; color:#374151; cursor:pointer; }
.btn.primary{ background:#0b57d0; color:#fff; border-color:#0b57d0; }
.btn.primary:hover{ background:#063e99; }
.editor{ height:220px; }
.code{ width:100%; height:100%; padding:10px; border:1px solid #e5e7eb; border-radius:8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size:13px; line-height:1.6; outline:none; overflow:auto; }
.result{ display:flex; flex-direction:column; min-height:0; }
.rhdr{ padding:8px 12px; background:#f8fafc; border-bottom:1px solid #e5e7eb; }
.rbody{ flex:1 1 auto; min-height:0; overflow:auto; padding:12px; }
.rtbl{ border-collapse:collapse; font-size:14px; }
.rtbl th,.rtbl td{ border:1px solid #e5e7eb; padding:6px 10px; white-space:nowrap; }
</style>

