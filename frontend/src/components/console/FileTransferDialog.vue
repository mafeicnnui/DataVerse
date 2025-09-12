<template>
  <div v-if="embedded || visible" :class="embedded ? 'ft-embed' : 'ft-overlay'">
    <div :class="['ft-dialog', { embed: embedded }]">
      <div class="ft-header">
        <div class="ft-title">文件传输</div>
        <div class="ft-actions">
          <button v-if="!embedded" class="icon-btn back" @click="onClose" :disabled="hasRunningTransfers()" :title="hasRunningTransfers()? '存在进行中的传输任务，无法关闭' : '返回'" aria-label="返回">
            <!-- 向上弯的返回箭头 -->
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 11l-4-4 4-4"/>
              <path d="M5 7h9a6 6 0 1 1 0 12h-3"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="ft-toolbar">
        <div class="left-tools">
          <button class="btn" @click="pickLocalRoot">📂 选择本地目录</button>
          <button class="btn" @click="pickLocalFiles">⬆️ 选择文件上传</button>
          <input ref="fileInput" type="file" multiple style="display:none" @change="onPickFiles" />
        </div>
        <div class="right-tools">
          <span class="hint">远程主机：{{ hostInfo.host }}:{{ hostInfo.port }}</span>
        </div>
      </div>
      <div class="ft-body" :style="{ '--leftPct': leftPanePct + '%', '--rightPct': (100-leftPanePct) + '%' }">
        <div class="pane left"
             @dragover.prevent
             @drop.prevent="onDropToLocal"
             :style="{ width: `calc(var(--leftPct) - 4px)` }">
          <div class="pane-title">本地</div>
          <div class="pathbar">
            <!-- 左侧按钮组：后退 / 前进 -->
            <div class="btn-group">
              <button class="icon-btn sm" :disabled="localHistIndex<=0" @click="localGoBack" title="后退">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
              </button>
              <button class="icon-btn sm" :disabled="localHistIndex>=localHistory.length-1" @click="localGoForward" title="前进">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>
              </button>
            </div>
            
            <!-- 本地路径：允许手动输入并回车跳转（运行中也允许本地导航） -->
            <input class="path-input current" v-model.trim="localPathInput" placeholder="例如: Projects 或 ..\\Docs；绝对路径请先选择该盘符根" @keydown.enter.prevent="goLocalTo" />
            <!-- 右侧按钮组：转到 / 刷新 -->
            <div class="btn-group">
              <button class="icon-btn sm" @click="goLocalTo" title="转到">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M13 5l7 7-7 7"/></svg>
              </button>
              <button class="icon-btn sm" @click="refreshLocal" title="刷新本地">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 1-9 9 9 9 0 1 1 6.36-15.36"/><path d="M22 4v6h-6"/></svg>
              </button>
            </div>
          </div>
          <div class="tree" v-if="localLoaded" @keydown.stop="onLocalKeydown" tabindex="0">
            <div class="list-wrap" ref="localListRef">
            <table class="ft-table">
              <thead>
                <tr>
                  <th class="col-name" @click="toggleLocalSort('name')">名称 <span class="sort" v-if="localSort.key==='name'">{{ localSort.asc?'▲':'▼' }}</span></th>
                  <th class="col-size" @click="toggleLocalSort('size')">大小 <span class="sort" v-if="localSort.key==='size'">{{ localSort.asc?'▲':'▼' }}</span></th>
                  <th class="col-time" @click="toggleLocalSort('mtime')">修改时间 <span class="sort" v-if="localSort.key==='mtime'">{{ localSort.asc?'▲':'▼' }}</span></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(n,idx) in localEntries" :key="n.path" :class="{ selected: idx===localSelIndex }"
                    draggable="true" @dragstart="onDragLocal(n)" @click="selectLocal(idx)" @dblclick="onLocalEnter(n)">
                  <td class="col-name"><span class="icon" :class="n.kind"></span><span class="name">{{ n.name }}</span></td>
                  <td class="col-size">{{ n.kind==='file' ? formatSize(n.size) : '-' }}</td>
                  <td class="col-time">{{ formatTime(n.mtime) }}</td>
                </tr>
              </tbody>
            </table>
            </div>
          </div>
          <div v-else class="empty">将自动尝试打开“桌面”。若浏览器未授权，请点击上方“选择本地目录”。</div>
        </div>
        <!-- 中间可拖拽分隔条 -->
        <div class="v-split" @mousedown="startHResize" title="拖动调整左右宽度" style="width: 4px; cursor: ew-resize;"></div>
        <div class="pane right"
             @dragover.prevent
             @drop.prevent="onDropToRemote"
             :style="{ width: `calc(var(--rightPct) - 4px)` }">
          <div class="pane-title">远程</div>
          <div class="pathbar">
            <!-- 左侧按钮组：后退 / 前进 -->
            <div class="btn-group">
              <button class="icon-btn sm" :disabled="remoteHistIndex<=0 || hasRunningTransfers()" @click="remoteGoBack" title="后退">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
              </button>
              <button class="icon-btn sm" :disabled="remoteHistIndex>=remoteHistory.length-1 || hasRunningTransfers()" @click="remoteGoForward" title="前进">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>
              </button>
            </div>
            
            <!-- 实时显示并可编辑远程路径（双向绑定） -->
            <input class="path-input" v-model.trim="remotePathInput" :readonly="hasRunningTransfers()" placeholder="/home/user 或 ~ / /var/log" @keydown.enter.prevent="goRemoteTo" />
            <!-- 右侧按钮组：转到 / 刷新 -->
            <div class="btn-group">
              <button class="icon-btn sm" @click="goRemoteTo" :disabled="hasRunningTransfers()" title="转到">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M13 5l7 7-7 7"/></svg>
              </button>
              <button class="icon-btn sm" @click="refreshRemote" :disabled="hasRunningTransfers()" title="刷新远程">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 1-9 9 9 9 0 1 1 6.36-15.36"/><path d="M22 4v6h-6"/></svg>
              </button>
            </div>
          </div>
          <div class="tree" v-if="remoteLoaded" @keydown.stop="onRemoteKeydown" tabindex="0">
            <div class="list-wrap" ref="remoteListRef">
            <table class="ft-table">
              <thead>
                <tr>
                  <th class="col-name" @click="toggleRemoteSort('name')">名称 <span class="sort" v-if="remoteSort.key==='name'">{{ remoteSort.asc?'▲':'▼' }}</span></th>
                  <th class="col-size" @click="toggleRemoteSort('size')">大小 <span class="sort" v-if="remoteSort.key==='size'">{{ remoteSort.asc?'▲':'▼' }}</span></th>
                  <th class="col-time" @click="toggleRemoteSort('mtime')">修改时间 <span class="sort" v-if="remoteSort.key==='mtime'">{{ remoteSort.asc?'▲':'▼' }}</span></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(r,idx) in remoteEntries" :key="r.path" :class="{ selected: idx===remoteSelIndex }"
                    draggable="true" @dragstart="onDragRemote(r)" @click="selectRemote(idx)" @dblclick.stop="onRemoteEnter(r)">
                  <td class="col-name" @dblclick.stop="onRemoteEnter(r)"><span class="icon" :class="r.kind"></span><span class="name">{{ r.name }}</span></td>
                  <td class="col-size">{{ r.kind==='file' ? formatSize(r.size) : '-' }}</td>
                  <td class="col-time">{{ formatTime(r.mtime) }}</td>
                </tr>
              </tbody>
            </table>
            </div>
          </div>
          <div v-else class="empty">
            <div v-if="remoteLoading">正在加载远程目录...</div>
            <div v-else>尝试加载远程目录失败或尚未实现后端接口。</div>
            <div class="tips">
              需要后端提供 SFTP/文件接口：
              <code>POST /api/ssh/sftp/list</code>, <code>/upload</code>, <code>/download</code>
            </div>
            <button class="btn" @click="refreshRemote">重试</button>
          </div>
        </div>
      </div>
      <div class="ft-resizer" @mousedown="startResizeFooter" title="拖动调整下方高度"></div>
      <!-- 底部区域：上方工具栏(标签+状态)，下方内容(传输/日志) -->
      <div class="ft-footer" :style="{height: footerHeight + 'px'}">
        <div class="ft-toolbar">
          <div class="ft-tabs">
            <button class="tab" :class="{active: txActiveTab==='transfer'}" @click="txActiveTab='transfer'">传输</button>
            <button class="tab" :class="{active: txActiveTab==='log'}" @click="txActiveTab='log'">日志</button>
          </div>
          <div class="status">{{ status }}</div>
        </div>
        <div class="ft-content">
          <div v-show="txActiveTab==='transfer'" class="transfers" :class="{empty: !transfers.length}">
            <table class="tx-table">
              <thead>
                <tr>
                  <th style="width:34%;">名称</th>
                  <th style="width:8%;">方向</th>
                  <th style="width:24%;">进度</th>
                  <th style="width:8%;">百分比</th>
                  <th style="width:10%;">速度</th>
                  <th style="width:8%;">剩余</th>
                  <th style="width:8%;">状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="tx in transfers" :key="tx.id">
                  <td class="tx-name" :title="tx.name">{{ tx.name }}</td>
                  <td>{{ tx.direction==='upload' ? '上传' : '下载' }}</td>
                  <td>
                    <div class="tx-bar"><i :style="{width: (Number(tx.progress||0)) + '%'}"></i></div>
                  </td>
                  <td>{{ (Number(tx.progress||0)).toFixed(0) }}%</td>
                  <td>{{ formatSpeed(tx.speed) }}</td>
                  <td>{{ formatETA(tx) }}</td>
                  <td>{{ tx.status }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-show="txActiveTab==='log'" class="tx-log">
            <pre class="log-view">{{ logs.join('\n') }}</pre>
          </div>
        </div>
      </div>
      <!-- 覆盖确认弹窗：作为对话框的最后子元素，覆盖整个窗口 -->
      <div v-if="ow.show" class="ow-mask">
        <div class="ow-dialog">
          <div class="ow-title">
            <svg class="ow-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <circle cx="12" cy="16" r="1"></circle>
            </svg>
            <span>目标已存在同名文件</span>
          </div>
          <div class="ow-body">
            <div class="row"><span class="label">名称</span><span class="val code" :title="ow.name">{{ ow.name }}</span></div>
            <div class="row"><span class="label">目标路径</span><span class="val code" :title="remotePath">{{ remotePath }}</span></div>
            <div class="tip">选择操作：<b>覆盖</b> 将替换远程同名文件；<b>取消</b> 则放弃本次上传。</div>
          </div>
          <div class="ow-actions">
            <button class="btn primary" @click="resolveOverwrite(true)">覆盖</button>
            <button class="btn ghost" @click="resolveOverwrite(false)">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed, nextTick } from 'vue'
import api from '../../api'

const props = defineProps({
  visible: { type: Boolean, default: false },
  hostInfo: { type: Object, default: () => ({ host: '', port: 22, user: '', auth: 'password' }) },
  embedded: { type: Boolean, default: false },
})
// 统一在脚本中通过 computed 使用 hostInfo.value，避免直接从 props 取值导致的未定义问题
const hostInfo = computed(() => props.hostInfo || {})
const emits = defineEmits(['close'])
function onClose(){
  if (props.embedded) { emits('close'); return }
  if (hasRunningTransfers()) { status.value = '存在进行中的传输任务，不能关闭窗口'; return }
  emits('close')
}

// —— 路径历史：本地/远程（用于“后退/前进”按钮） ——
const localHistory = ref([]) // string[]，展示用路径
const localHistIndex = ref(-1)
function pushLocalHistory(path){
  const p = String(path||''); if (!p) return
  if (localHistIndex.value >= 0 && localHistory.value[localHistIndex.value] === p) return
  if (localHistIndex.value < localHistory.value.length - 1){
    localHistory.value = localHistory.value.slice(0, localHistIndex.value + 1)
  }
  localHistory.value.push(p)
  localHistIndex.value = localHistory.value.length - 1
}
async function localGoBack(){
  if (localHistIndex.value <= 0) return
  localHistIndex.value--
  const target = localHistory.value[localHistIndex.value] || ''
  await goLocalToDisplayPath(target)
}
async function localGoForward(){
  if (localHistIndex.value >= localHistory.value.length - 1) return
  localHistIndex.value++
  const target = localHistory.value[localHistIndex.value] || ''
  await goLocalToDisplayPath(target)
}

// 直接根据“展示路径”跳转（用于历史前进/后退），从授权根开始重建句柄栈，避免路径重复叠加
async function goLocalToDisplayPath(displayed){
  try{
    const raw = String(displayed||'').trim()
    if (!raw) return
    const base = localAuthorizedRoot.value || localRootHandle.value
    if (!base){ status.value = '请先点击“选择本地目录”授予访问权限'; return }
    const parts = raw.replace(/^[\\/]+|[\\/]+$/g,'').split(/[\\/]+/).filter(Boolean)
    let h = base
    const stack = [base]
    let acc = ''
    for (const seg of parts){
      h = await h.getDirectoryHandle(seg, { create: false })
      stack.push(h)
      acc = acc ? (acc + '/' + seg) : seg
    }
    localEntries.value = await readLocalDirectory(h)
    localRootHandle.value = h
    localHandleStack.value = stack
    localRootPath.value = acc
    localFullPath.value = raw
    localPathInput.value = raw
    localLoaded.value = true
    status.value = ''
  }catch(e){ status.value = '无法进入本地目录（历史路径可能越出授权根或已不可访问）' }
}

const remoteHistory = ref([])
const remoteHistIndex = ref(-1)
function pushRemoteHistory(path){
  const p = String(path||''); if (!p) return
  if (remoteHistIndex.value >= 0 && remoteHistory.value[remoteHistIndex.value] === p) return
  if (remoteHistIndex.value < remoteHistory.value.length - 1){
    remoteHistory.value = remoteHistory.value.slice(0, remoteHistIndex.value + 1)
  }
  remoteHistory.value.push(p)
  remoteHistIndex.value = remoteHistory.value.length - 1
}
function remoteGoBack(){
  if (hasRunningTransfers()) return
  if (remoteHistIndex.value <= 0) return
  remoteHistIndex.value--
  remotePathInput.value = remoteHistory.value[remoteHistIndex.value] || ''
  if (typeof goRemoteTo === 'function') goRemoteTo()
}
function remoteGoForward(){
  if (hasRunningTransfers()) return
  if (remoteHistIndex.value >= remoteHistory.value.length - 1) return
  remoteHistIndex.value++
  remotePathInput.value = remoteHistory.value[remoteHistIndex.value] || ''
  if (typeof goRemoteTo === 'function') goRemoteTo()
}

// 列表滚动容器 refs（固定表头，仅表体滚动；目录变更时滚到首行）
const localListRef = ref(null)
const remoteListRef = ref(null)
function scrollListsTop(){
  try{ if (localListRef.value) localListRef.value.scrollTop = 0 }catch{}
  try{ if (remoteListRef.value) remoteListRef.value.scrollTop = 0 }catch{}
}
async function goLocalTo(){
  if (!localRootHandle.value) { status.value = '请先点击“选择本地目录”授予访问权限'; return }
  const raw = (localPathInput.value||'').trim()
  if (!raw) return
  // 规范分隔符，支持 \\ 或 /
  let norm = raw.replace(/\\+/g,'/')
  // 若输入为绝对路径（盘符），尝试将其转为“相对当前授权根”的子路径（若不是其子路径，会报错并提示）
  const isAbs = /^[A-Za-z]:(?:\\|\/)/.test(raw) || /^[A-Za-z]:\//.test(norm)
  const fromRoot = isAbs || norm.startsWith('/')
  if (isAbs) {
    // 去掉盘符前缀 D:/
    norm = norm.replace(/^[A-Za-z]:\//, '')
  }
  const p = norm.replace(/^\/*|\/*$/g,'')
  try{
    // 选择起点：绝对路径或以 / 开头，则从“授权根”起步；否则从当前目录起步
    let h = fromRoot && localAuthorizedRoot.value ? localAuthorizedRoot.value : localRootHandle.value
    // 重置栈为起点
    localHandleStack.value = [h]
    if (p === '..'){
      // 返回上一级：使用句柄栈
      if (localHandleStack.value.length > 1){
        try{
          localHandleStack.value.pop()
          const parent = localHandleStack.value[localHandleStack.value.length-1]
          localEntries.value = await readLocalDirectory(parent)
          localRootHandle.value = parent
          // 修剪显示路径
          const idx = localRootPath.value.lastIndexOf('/')
          localRootPath.value = idx>0 ? localRootPath.value.slice(0, idx) : ''
          localFullPath.value = localRootPath.value || (parent.name||'')
          localPathInput.value = localFullPath.value
          localLoaded.value = true
          status.value = ''
          pushLocalHistory(localFullPath.value)
          return
        }catch{}
      }
      status.value = '已在根目录'
      return
    }
    if (p === '.' || p === ''){
      // 刷新当前目录
      localEntries.value = await readLocalDirectory(h)
      localPathInput.value = localRootPath.value
      localLoaded.value = true
      status.value = ''
      return
    }
    const parts = p.split('/').filter(Boolean)
    for (const seg of parts){
      h = await h.getDirectoryHandle(seg, { create: false })
      localHandleStack.value.push(h)
    }
    localEntries.value = await readLocalDirectory(h)
    localRootHandle.value = h
    // 显示路径：如果用户输入的是绝对路径，则优先展示用户输入（规范为反斜杠），否则展示累加路径
    if (isAbs) {
      const displayed = raw.replace(/\//g,'\\')
      localFullPath.value = displayed
      localRootPath.value = displayed
      localPathInput.value = displayed
    } else {
      localRootPath.value = (localRootPath.value ? (localRootPath.value + '/') : '') + p
      localFullPath.value = localRootPath.value
      localPathInput.value = localFullPath.value
    }
    localLoaded.value = true
    status.value = ''
    pushLocalHistory(localFullPath.value)
  }catch(e){ status.value = '无法进入本地目录（请确认路径在已授权根目录之下，并校验大小写/权限）' }
}

async function goLocalUp(){
  try{
    if (hasRunningTransfers()) { status.value = '存在进行中的传输任务，禁止返回上一级'; return }
    if (localHandleStack.value.length > 1){
      localHandleStack.value.pop()
      const parent = localHandleStack.value[localHandleStack.value.length-1]
      localEntries.value = await readLocalDirectory(parent)
      localRootHandle.value = parent
      const idx = (localRootPath.value||'').lastIndexOf('/')
      localRootPath.value = idx>0 ? localRootPath.value.slice(0, idx) : ''
      localFullPath.value = localRootPath.value || (parent.name||'')
      localPathInput.value = localFullPath.value
      localLoaded.value = true
      status.value = ''
    } else {
      status.value = '已在根目录'
    }
  }catch(e){ status.value = '返回上级失败' }
}

// 刷新本地目录
async function refreshLocal(){
  try{
    const h = localRootHandle.value
    if (!h) { status.value = '尚未选择本地目录'; return }
    localEntries.value = await readLocalDirectory(h)
    localLoaded.value = true
    status.value = ''
  }catch(e){ status.value = '刷新本地目录失败' }
}

// 状态
const status = ref('')
// 传输队列：{ id, name, direction:'upload'|'download', size, loaded, progress, speed, status:'running'|'done'|'error' }
const transfers = ref([])
const txActiveTab = ref('transfer')
const logs = ref([])
function addLog(msg){
  const t = new Date(); const h = String(t.getHours()).padStart(2,'0'); const m = String(t.getMinutes()).padStart(2,'0'); const s = String(t.getSeconds()).padStart(2,'0')
  logs.value.push(`[${h}:${m}:${s}] ${msg}`)
  if (logs.value.length > 500) logs.value.shift()
}
// 底部面板高度（可拖动调整），默认增加 50px
const footerHeight = ref(150)
function startResizeFooter(e){
  try{
    const startY = e.clientY
    const startH = footerHeight.value
    const dialog = e.currentTarget?.closest?.('.ft-dialog')
    const maxH = Math.max(80, Math.floor((dialog?.clientHeight||640) * 0.6))
    const onMove = (ev)=>{
      const dy = (ev.clientY||0) - startY
      let h = startH + dy
      if (h < 60) h = 60
      if (h > maxH) h = maxH
      footerHeight.value = h
    }
    const onUp = ()=>{ window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp) }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }catch{}
}
const remoteLoading = ref(false)
const fileInput = ref(null)
// 覆盖确认弹窗状态
const ow = reactive({ show:false, name:'', resolver:null })
function askOverwrite(name){
  ow.show = true; ow.name = name
  return new Promise(resolve=>{ ow.resolver = resolve })
}
function resolveOverwrite(val){ if (ow.resolver) ow.resolver(val); ow.resolver=null; ow.show=false }
// 远程目录缓存与并发控制
const remoteCache = reactive({}) // key: path -> entries
let remoteReqToken = null

// 本地侧（File System Access API）
const localRootHandle = ref(null)
const localAuthorizedRoot = ref(null) // 首次授权的根目录句柄，用于绝对路径跳转的起点
const localRootPath = ref('')
const localEntries = ref([]) // 当前根下的一级条目
const localLoaded = ref(false)
const localSubPath = ref('')
const localSort = reactive({ key: 'name', asc: true })
const localSelIndex = ref(-1)
const localFullPath = ref('')
const localPathInput = ref('')
const localHandleStack = ref([]) // 记录从根到当前的句柄路径
let dragPayload = null // { side: 'local'|'remote', entry }

async function pickLocalRoot(){
  status.value = ''
  try {
    if ('showDirectoryPicker' in window){
      const handle = await window.showDirectoryPicker({ startIn: 'desktop' }).catch(async ()=>{
        // 某些浏览器不支持 startIn，退化为无参
        return await window.showDirectoryPicker()
      })
      localRootHandle.value = handle
      localAuthorizedRoot.value = handle
      localRootPath.value = handle.name
      localFullPath.value = handle.name
      localPathInput.value = localFullPath.value
      localEntries.value = await readLocalDirectory(handle)
      localLoaded.value = true
      localHandleStack.value = [handle]
    } else {
      alert('当前浏览器不支持选择目录，请使用新版 Chrome/Edge。')
    }
  } catch(e){ status.value = '已取消或无权限' }
}

function pickLocalFiles(){
  fileInput.value && fileInput.value.click()
}

async function onPickFiles(e){
  const files = Array.from(e?.target?.files || [])
  if (!files.length) return
  // 批量顺序上传
  for (const f of files){
    try{
      status.value = `上传中：${f.name}`
      await uploadFile(remotePath.value, f)
      status.value = `已上传 ${f.name}`
    }catch(err){
      const msg = err?.response?.data?.detail || err?.message || err
      status.value = `上传失败：${f.name}（${msg}）`
    }
  }
  // 统一刷新
  await refreshRemote()
  try{ e.target.value = '' }catch{}
}

async function readLocalDirectory(dirHandle){
  const list = []
  try{
    for await (const [name, handle] of dirHandle.entries()){
      const item = { name, path: name, handle, kind: handle.kind, size: null, mtime: null }
      if (handle.kind === 'file'){
        try { const f = await handle.getFile(); item.size = f.size; item.mtime = Math.floor((f.lastModified||0)/1000) } catch {}
      }
      list.push(item)
    }
  }catch{}
  return applyLocalSort(list)
}

function applyLocalSort(arr){
  const a = Array.isArray(arr) ? [...arr] : []
  const key = localSort.key
  const asc = !!localSort.asc
  a.sort((x,y)=>{
    // 目录优先
    if (x.kind!==y.kind) return x.kind==='directory' ? -1 : 1
    let vx, vy
    if (key==='size'){ vx = x.size||0; vy = y.size||0 }
    else if (key==='mtime'){ vx = x.mtime||0; vy = y.mtime||0 }
    else { vx = (x.name||''); vy = (y.name||''); return asc ? vx.localeCompare(vy) : vy.localeCompare(vx) }
    return asc ? (vx-vy) : (vy-vx)
  })
  return a
}

function toggleLocalSort(key){
  if (localSort.key === key) { localSort.asc = !localSort.asc } else { localSort.key = key; localSort.asc = true }
  localEntries.value = applyLocalSort(localEntries.value)
}

function selectLocal(idx){ localSelIndex.value = idx }
function onLocalEnter(n){ if (n?.kind==='directory') expandLocalLikeReload(n) }
function onLocalKeydown(e){
  const len = localEntries.value.length
  if (!len) return
  if (e.key==='ArrowDown'){ e.preventDefault(); localSelIndex.value = Math.min(len-1, (localSelIndex.value<0?0:localSelIndex.value+1)) }
  else if (e.key==='ArrowUp'){ e.preventDefault(); localSelIndex.value = Math.max(0, (localSelIndex.value<=0?0:localSelIndex.value-1)) }
  else if (e.key==='Enter' && localSelIndex.value>=0){ const n = localEntries.value[localSelIndex.value]; onLocalEnter(n) }
}

async function expandLocalLikeReload(node){
  // 进入子目录：更新句柄栈与显示路径
  try {
    const h = node?.handle
    if (!h || node.kind!=='directory') return
    localEntries.value = await readLocalDirectory(h)
    localRootHandle.value = h
    // 栈：若为空，初始化；否则压入
    if (!Array.isArray(localHandleStack.value) || localHandleStack.value.length === 0) {
      localHandleStack.value = [h]
    } else {
      localHandleStack.value.push(h)
    }
    localRootPath.value = localRootPath.value ? (localRootPath.value + '/' + node.name) : node.name
    localPathInput.value = localRootPath.value
    localLoaded.value = true
    status.value = ''
    try{ pushLocalHistory(localPathInput.value) }catch{}
  } catch { status.value = '进入目录失败' }
}

async function expandLocal(node){
  if (node.kind !== 'directory') return
  if (!node.children){
    try{
      node.children = []
      for await (const [name, handle] of node.handle.entries()){
        node.children.push({ name, path: node.path + '/' + name, handle, kind: handle.kind })
      }
      node.children.sort((a,b)=> (a.kind===b.kind? a.name.localeCompare(b.name) : (a.kind==='directory'?-1:1)))
    }catch{}
  }
  node.expanded = !node.expanded
}

function onDragLocal(entry){ dragPayload = { side: 'local', entry } }
function onDragRemote(entry){ dragPayload = { side: 'remote', entry } }

async function onDropToRemote(ev){
  if (!dragPayload || dragPayload.side !== 'local') return
  const entry = dragPayload.entry
  try{
    if (entry.kind === 'file'){
      const file = await entry.handle.getFile()
      await uploadFile(remotePath.value, file)
      status.value = `已上传 ${entry.name}`
      await refreshRemote()
    } else {
      status.value = '暂不支持目录整体上传（可点进目录逐个上传文件）'
    }
  } catch(e){
    const msg = e?.response?.data?.detail || e?.message || e
    status.value = '上传失败：' + msg
  }
  finally{ dragPayload = null }
}

async function onDropToLocal(ev){
  if (!dragPayload || dragPayload.side !== 'remote') return
  const entry = dragPayload.entry
  try{
    const blob = await downloadFile(entry.path)
    if (!blob){ status.value = '下载失败'; return }
    if ('showSaveFilePicker' in window){
      const sh = await window.showSaveFilePicker({ suggestedName: entry.name })
      const w = await sh.createWritable()
      await w.write(blob)
      await w.close()
    } else {
      // 兜底：a 标签下载
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = entry.name
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    }
    status.value = `已下载 ${entry.name}`
  } catch(e){ status.value = '下载失败：' + (e?.message||e) }
  finally{ dragPayload = null }
}

// 远程侧（需后端配合）
const remotePath = ref('~')
const remoteEntries = ref([])
const remoteLoaded = ref(false)
const remotePathInput = ref('')
const remoteSort = reactive({ key: 'name', asc: true })
const remoteSelIndex = ref(-1)

// 左右分栏宽度（百分比），默认 50/50；通过中间分隔条拖动调整
const leftPanePct = ref(50)
const draggingH = ref(false)
function startHResize(e){
  try{
    draggingH.value = true
    const wrap = e.currentTarget?.closest?.('.ft-body')
    const rect = wrap?.getBoundingClientRect?.()
    const startX = e.clientX
    const startPct = leftPanePct.value
    const onMove = (ev)=>{
      if (!rect) return
      const dx = (ev.clientX - startX)
      const deltaPct = rect.width ? (dx / rect.width) * 100 : 0
      let p = startPct + deltaPct
      if (p < 20) p = 20
      if (p > 80) p = 80
      leftPanePct.value = Math.round(p)
    }
    const onUp = ()=>{
      draggingH.value = false
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }catch{}
}

// 初次挂载与参数变化时，尝试加载远程目录
onMounted(() => {
  try { remotePathInput.value = String(remotePath.value || '~') } catch {}
  refreshRemote()
})
watch(() => props.visible, (v) => { if (v) refreshRemote() })
watch(hostInfo, () => { if (props.visible) refreshRemote() }, { deep: true })

async function refreshRemote(){
  if (!hostInfo.value) return
  const p = String(remotePath.value||'~')
  // 先用缓存即时展示，提升双击体感速度
  const cached = remoteCache[p]
  if (cached) { remoteEntries.value = cached; remoteLoaded.value = true }
  remoteLoading.value = true
  const myToken = {}
  remoteReqToken = myToken
  try{
    const fd = new FormData()
    fd.append('host', hostInfo.value.host)
    fd.append('port', hostInfo.value.port)
    fd.append('user', hostInfo.value.user)
    fd.append('auth', hostInfo.value.auth||'password')
    if ((hostInfo.value.auth||'password') === 'password'){
      if (hostInfo.value.pass) fd.append('password', hostInfo.value.pass)
    } else {
      try{
        const kb64 = btoa(hostInfo.value.privateKey || '')
        if (kb64) fd.append('key_b64', kb64)
        if (hostInfo.value.keyPass) fd.append('key_pass', hostInfo.value.keyPass)
      }catch{}
    }
    fd.append('path', p)
    const { data } = await api.post('/ssh/sftp/list', fd)
    if (remoteReqToken !== myToken) return // 已被后续请求覆盖
    remoteEntries.value = (data||[])
    remoteCache[p] = remoteEntries.value
    remoteLoaded.value = true
  }catch(e){
    if (remoteReqToken === myToken){ remoteLoaded.value = false }
  }finally{ if (remoteReqToken === myToken) remoteLoading.value = false }
}

function goRemoteTo(){
  const v = (remotePathInput.value||'').trim()
  if (!v) return
  remotePath.value = v
  try{ pushRemoteHistory(remotePath.value) }catch{}
  refreshRemote()
}

function applyRemoteSort(arr){
  const a = Array.isArray(arr) ? [...arr] : []
  const key = remoteSort.key
  const asc = !!remoteSort.asc
  a.sort((x,y)=>{
    if (x.kind!==y.kind) return x.kind==='directory' ? -1 : 1
    let vx, vy
    if (key==='size'){ vx = x.size||0; vy = y.size||0 }
    else if (key==='mtime'){ vx = x.mtime||0; vy = y.mtime||0 }
    else { vx = (x.name||''); vy = (y.name||''); return asc ? vx.localeCompare(vy) : vy.localeCompare(vx) }
    return asc ? (vx-vy) : (vy-vx)
  })
  return a
}

function toggleRemoteSort(key){
  if (remoteSort.key === key) { remoteSort.asc = !remoteSort.asc } else { remoteSort.key = key; remoteSort.asc = true }
  remoteEntries.value = applyRemoteSort(remoteEntries.value)
}

function selectRemote(idx){ remoteSelIndex.value = idx }
function onRemoteKeydown(e){
  const len = remoteEntries.value.length
  if (!len) return
  if (e.key==='ArrowDown'){ e.preventDefault(); remoteSelIndex.value = Math.min(len-1, (remoteSelIndex.value<0?0:remoteSelIndex.value+1)) }
  else if (e.key==='ArrowUp'){ e.preventDefault(); remoteSelIndex.value = Math.max(0, (remoteSelIndex.value<=0?0:remoteSelIndex.value-1)) }
  else if (e.key==='Enter' && remoteSelIndex.value>=0){ const n = remoteEntries.value[remoteSelIndex.value]; onRemoteEnter(n) }
  else if ((e.key==='Backspace' || (e.altKey && e.key==='ArrowUp'))) { e.preventDefault(); goRemoteUp() }
}

function formatSize(n){
  const v = Number(n||0)
  if (!isFinite(v) || v<=0) return '-'
  const units = ['B','KB','MB','GB','TB']
  let i=0, x=v
  while (x>=1024 && i<units.length-1){ x/=1024; i++ }
  return (x>=100? x.toFixed(0) : x>=10? x.toFixed(1) : x.toFixed(2)) + ' ' + units[i]
}
function formatTime(ts){
  const t = Number(ts||0)
  if (!isFinite(t) || t<=0) return ''
  try { const d = new Date(t*1000); const pad = (n)=> String(n).padStart(2,'0'); return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}` } catch { return '' }
}

function formatSpeed(bps){
  const v = Number(bps||0)
  if (!isFinite(v) || v<=0) return '-'
  const units = ['B/s','KB/s','MB/s','GB/s']
  let i=0, x=v
  while (x>=1024 && i<units.length-1){ x/=1024; i++ }
  return (x>=100? x.toFixed(0) : x>=10? x.toFixed(1) : x.toFixed(2)) + ' ' + units[i]
}

function formatETA(tx){
  try{
    const size = Number(tx.size||0), loaded = Number(tx.loaded||0), spd = Number(tx.speed||0)
    if (!isFinite(size) || size<=0 || !isFinite(spd) || spd<=0) return '-'
    let remain = Math.max(0, (size - loaded) / spd)
    const hh = Math.floor(remain/3600); remain -= hh*3600
    const mm = Math.floor(remain/60); const ss = Math.floor(remain - mm*60)
    const pad = (n)=> String(n).padStart(2,'0')
    return hh>0 ? `${hh}:${pad(mm)}:${pad(ss)}` : `${mm}:${pad(ss)}`
  }catch{ return '-' }
}

function onRemoteEnter(node){
  if (!node) return
  if (hasRunningTransfers()) { status.value = '存在进行中的传输任务，禁止切换远程目录'; return }
  if (node.kind==='directory'){
    remotePath.value = node.path
    remotePathInput.value = remotePath.value
    try{ pushRemoteHistory(remotePath.value) }catch{}
    refreshRemote()
  } else { downloadFile(node.path).then(blob=>{ if (blob) status.value = `已下载 ${node.name}` }).catch(()=>{}) }
}

function goRemoteUp(){
  if (!remotePath.value || remotePath.value==='/' || remotePath.value==='~') return
  const p = remotePath.value.replace(/\/+/g,'/')
  const idx = p.lastIndexOf('/')
  remotePath.value = idx>0 ? p.slice(0, idx) : '/'
  remotePathInput.value = remotePath.value
  try{ pushRemoteHistory(remotePath.value) }catch{}
  refreshRemote()
}

async function uploadFile(targetDir, file){
  // 覆盖确认：若目标目录已有同名文件，提示用户
  const exists = (remoteEntries.value||[]).some(e => e.kind==='file' && e.name===file.name)
  let willOverwrite = false
  if (exists){
    const ok = await askOverwrite(file.name)
    if (!ok){ addLog(`已取消上传: ${file.name}`); status.value = '已取消'; return }
    willOverwrite = true
  }
  const txid = `${Date.now()}:${Math.random().toString(36).slice(2,8)}`
  // 重要：将传输项做 reactive 包裹，确保进度/状态更新能触发视图更新
  const tx = reactive({ id: txid, name: file.name, direction: 'upload', size: file.size||0, loaded: 0, progress: 0, speed: 0, status: 'running' })
  transfers.value.unshift(tx)
  const startedAt = Date.now()
  let lastT = Date.now(), lastLoaded = 0
  // 进度/速度优先以远端实测为准；一旦启用远端轮询，忽略本地 onprogress 的速度计算
  let preferRemote = false
  let lastLocalLoaded = 0
  let lastRemoteLoaded = 0
  // 记录最近一次远端观测到的字节数（用于限制本地进度不超过远端）
  let remoteObserved = 0
  // 统一的进度更新：只允许单调递增，避免出现先到高值再回落
  function updateByLoaded(loaded, total){
    try{
      const safeTotal = total || 0
      let nextLoaded = Math.max(0, Math.min(safeTotal, Number(loaded||0)))
      // 单调递增，不回退
      if ((tx.loaded||0) > nextLoaded) nextLoaded = tx.loaded||0
      const now = Date.now()
      const dt = (now - lastT)/1000
      const bytes = Math.max(0, nextLoaded - (tx.loaded||0))
      tx.loaded = nextLoaded
      const nextProg = safeTotal ? Math.min(100, (nextLoaded/safeTotal*100)) : 0
      tx.progress = Math.max(tx.progress||0, nextProg)
      if (dt>0 && bytes>=0) tx.speed = bytes/dt
      lastT = now; lastLoaded = nextLoaded
    }catch{}
  }
  // 看门狗：长时间无进度时提示
  let stallTimer = null
  const armStall = () => {
    clearTimeout(stallTimer)
    stallTimer = setTimeout(()=>{
      if (tx.status === 'running' && (tx.progress||0) < 1) {
        addLog(`等待服务器响应中…（可能在建立 SFTP 连接或权限校验）: ${file.name}`)
        console.warn('[FileTransfer] still waiting server response')
      }
    }, 8000)
  }
  armStall()
  const form = new FormData()
  form.append('file', file)
  form.append('host', hostInfo.value.host)
  form.append('port', hostInfo.value.port)
  form.append('user', hostInfo.value.user)
  form.append('auth', hostInfo.value.auth||'password')
  if ((hostInfo.value.auth||'password') === 'password'){
    if (hostInfo.value.pass) form.append('password', hostInfo.value.pass)
  } else {
    try{
      const kb64 = btoa(hostInfo.value.privateKey || '')
      if (kb64) form.append('key_b64', kb64)
      if (hostInfo.value.keyPass) form.append('key_pass', hostInfo.value.keyPass)
    }catch{}
  }
  form.append('path', targetDir)
  if (willOverwrite) form.append('overwrite', 'true')
  try{
    addLog(`开始上传: ${file.name} -> ${targetDir}`)
    if (willOverwrite) addLog(`目标已存在同名文件，将覆盖: ${file.name}`)
    console.log('[FileTransfer] start upload', { name: file.name, size: file.size, targetDir })
    // 使用原生 XHR 确保 onprogress 可用，并尽快发起请求
    await new Promise((resolve, reject) => {
      try{
        const xhr = new XMLHttpRequest()
        xhr.open('POST', '/api/ssh/sftp/upload', true)
        xhr.timeout = 5 * 60 * 1000
        let lastEmitPct = -1
        // 统一的“以远端文件大小为准”的轮询器：避免本地缓冲导致 100% 假象
        let pollTimer = null
        const pollRemoteOnce = async () => {
          try{
            const fd = new FormData()
            fd.append('host', hostInfo.value.host)
            fd.append('port', hostInfo.value.port)
            fd.append('user', hostInfo.value.user)
            fd.append('auth', hostInfo.value.auth||'password')
            if ((hostInfo.value.auth||'password') === 'password'){
              if (hostInfo.value.pass) fd.append('password', hostInfo.value.pass)
            } else {
              try{
                const kb64 = btoa(hostInfo.value.privateKey || '')
                if (kb64) fd.append('key_b64', kb64)
                if (hostInfo.value.keyPass) fd.append('key_pass', hostInfo.value.keyPass)
              }catch{}
            }
            fd.append('path', targetDir)
            const { data } = await api.post('/ssh/sftp/list', fd)
            const list = Array.isArray(data)?data:[]
            const item = list.find(e => e && e.kind==='file' && e.name===file.name)
            if (item){
              const total = file.size || 0
              // 兼容后端返回 size 为字符串的情况
              let sz = (item && (item.size ?? item.Size ?? item.length ?? item.Length))
              let num = Number(sz)
              if (!Number.isFinite(num)){
                try{ num = parseInt(String(sz||'').replace(/[^0-9]/g,''),10) }catch{ num = 0 }
              }
              const remoteLoaded = Math.max(0, Math.min(total, num||0))
              // 以远端为准：不要和本地 lastLoaded 取最大，否则会被本地100%“顶满”
              const loadedNow = remoteLoaded
              preferRemote = true
              lastRemoteLoaded = remoteLoaded
              remoteObserved = remoteLoaded
              updateByLoaded(loadedNow, total)
            }
          }catch{}
        }
        const startPolling = () => { if (!pollTimer) pollTimer = setInterval(pollRemoteOnce, 1000) }
        xhr.upload.onloadstart = () => {
          try{
            tx.loaded = 0
            tx.progress = 0 // 从 0% 开始显示
            addLog('已开始发送数据（可能先进入本地/代理缓冲）')
          }catch{}
        }
        xhr.upload.onprogress = (e) => {
          try{
            const total = e.total || file.size || 0
            // 注意：本地发送进度仅作为“早期反馈”，一旦拿到远端进度，就以远端为准
            const localLoaded = e.loaded || 0
            lastLocalLoaded = localLoaded
            if (!preferRemote){
              // 恢复为 95% 上限：在未拿到远端进度前，本地进度最多显示到 95%
              const localPct = total ? (localLoaded/total*100) : 0
              const cappedPct = Math.min(localPct, 95)
              const cappedLoaded = Math.floor((cappedPct/100) * (total||0))
              // 额外限制：不超过“已观测到的远端字节数”（避免出现 95% 但远端只有几 MB 的错觉）
              const boundedLoaded = Math.min(cappedLoaded, remoteObserved || 0)
              updateByLoaded(boundedLoaded, total)
            }
            armStall()
            const pct = Math.floor(tx.progress || 0)
            if (pct !== lastEmitPct && (pct % 10 === 0 || pct === 1)){
              console.log('[FileTransfer] progress', pct+'%')
              lastEmitPct = pct
            }
          }catch{}
        }
        // 无论是否触发 onprogress，都启动远端轮询用于校正（1s一次）
        startPolling()
        xhr.onerror = () => { if (pollTimer) clearInterval(pollTimer); reject(new Error('网络错误')) }
        xhr.ontimeout = () => { if (pollTimer) clearInterval(pollTimer); reject(new Error('上传超时')) }
        xhr.onload = () => {
          const finalize = async () => {
            try{
              // 后端 HTTP 已返回，但远端写入可能仍在进行：等待远端文件大小到达目标
              const total = file.size || 0
              let attempts = 0
              while (attempts < 120) { // 最多等2分钟
                await pollRemoteOnce()
                if ((tx.loaded||0) >= total) break
                await new Promise(r => setTimeout(r, 1000))
                attempts++
              }
            } finally {
              if (pollTimer) clearInterval(pollTimer)
            }
          }
          if (xhr.status >= 200 && xhr.status < 300) {
            finalize().then(()=>resolve(undefined)).catch(()=>resolve(undefined))
          }
          else reject(new Error(`HTTP ${xhr.status}`))
        }
        xhr.send(form)
      }catch(ex){ reject(ex) }
    })
    tx.status = 'done'; tx.progress = 100; tx.speed = 0
    addLog(`上传完成: ${file.name}`)
    console.log('[FileTransfer] upload done', { name: file.name })
    // 上传成功后刷新远程目录，确保能看到新文件
    try{ await refreshRemote() }catch{}
  }catch(err){
    tx.status = 'error'
    tx.speed = 0
    const msg = err?.response?.data?.detail || err?.message || String(err)
    status.value = `上传失败：${file.name}（${msg}）`
    addLog(`上传失败: ${file.name} - ${msg}`)
    console.error('[FileTransfer] upload error', err)
  }
  finally{
    clearTimeout(stallTimer)
  }
}

async function downloadFile(path){
  try{
    const base = path.split('/')
    const name = base[base.length-1] || 'download.bin'
    const txid = `${Date.now()}:${Math.random().toString(36).slice(2,8)}`
    const tx = { id: txid, name, direction: 'download', size: null, loaded: null, progress: null, speed: null, status: 'running' }
    transfers.value.unshift(tx)
    const fd = new FormData()
    fd.append('host', hostInfo.value.host)
    fd.append('port', hostInfo.value.port)
    fd.append('user', hostInfo.value.user)
    fd.append('auth', hostInfo.value.auth)
    fd.append('path', path)
    if ((hostInfo.value.auth||'password') === 'password'){
      if (hostInfo.value.pass) fd.append('password', hostInfo.value.pass)
    } else {
      try{
        const kb64 = btoa(hostInfo.value.privateKey || '')
        if (kb64) fd.append('key_b64', kb64)
        if (hostInfo.value.keyPass) fd.append('key_pass', hostInfo.value.keyPass)
      }catch{}
    }
    const { data } = await api.post('/ssh/sftp/download', fd, { responseType: 'blob' })
    tx.status = 'done'; tx.progress = 100; tx.speed = 0
    return data
  }catch(e){ return null }
}

watch(()=>props.visible, async (v)=>{ 
  if(v){ 
    // 远程默认 ~（兜底初始化）
    if (!remotePath.value) remotePath.value = '~'
    remotePathInput.value = remotePath.value
    try{ pushRemoteHistory(remotePath.value) }catch{}
    try{ await refreshRemote() }catch{}
    // 本地：尝试自动打开桌面（需要权限）
    if (!localLoaded.value) {
      try {
        if ('showDirectoryPicker' in window) {
          const h = await window.showDirectoryPicker({ startIn: 'desktop' }).catch(()=>null)
          if (h) {
            localRootHandle.value = h
            localAuthorizedRoot.value = h
            localRootPath.value = h.name
            localFullPath.value = h.name
            localEntries.value = await readLocalDirectory(h)
            localLoaded.value = true
            localHandleStack.value = [h]
            try{ pushLocalHistory(localFullPath.value) }catch{}
          }
        }
      } catch {}
    }
  } 
})

onMounted(()=>{})

function hasRunningTransfers(){
  try{ return (transfers.value||[]).some(t => t && t.status === 'running') }catch{ return false }
}
</script>

<style scoped>
/* 底部内容容器：必须是 flex 且允许收缩，日志才能出现纵向滚动条 */
.ft-content{ flex:1; min-height:0; display:flex; width:100%; gap:12px; overflow-x:hidden; }
.ow-mask{ position:fixed; inset:0; background:rgba(15,23,42,.35); display:flex; align-items:center; justify-content:center; z-index:200100; }
.ow-dialog{ width:min(520px, 92vw); max-width:680px; background:#ffffff; color:#0f172a; border-radius:12px; box-shadow:0 20px 60px rgba(0,0,0,.28), 0 4px 16px rgba(0,0,0,.12); overflow:hidden; border:1px solid #e5e7eb; animation:ow-pop .14s ease-out; }
.ow-title{ display:flex; align-items:center; gap:8px; padding:12px 16px; font-weight:600; background:linear-gradient(180deg,#f8fafc,#eef2ff); border-bottom:1px solid #e5e7eb; color:#0b57d0; }
.ow-icon{ color:#0b57d0; }
.ow-body{ padding:14px 16px 6px; }
.ow-body .row{ display:flex; align-items:center; gap:10px; margin-bottom:8px; }
.ow-body .label{ width:74px; color:#64748b; flex:0 0 auto; }
.ow-body .val{ flex:1; min-width:0; color:#0f172a; }
.ow-body .code{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; background:#f8fafc; border:1px solid #e5e7eb; border-radius:6px; padding:4px 6px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.ow-body .tip{ margin-top:6px; color:#475569; font-size:12px; }
.ow-actions{ display:flex; justify-content:flex-end; gap:10px; padding:10px 16px 16px; border-top:1px solid #e5e7eb; background:#fff; }
.btn.primary{ background:#0b57d0; color:#ffffff; border-color:#0b57d0; }
.btn.primary:hover{ background:#0a4fc0; border-color:#0a4fc0; }
.btn.ghost{ background:#ffffff; color:#0b57d0; border-color:#93c5fd; }
.btn.ghost:hover{ background:#f1f5ff; }
@keyframes ow-pop{ from{ transform:translateY(6px) scale(.98); opacity:.6;} to{ transform:translateY(0) scale(1); opacity:1;} }
.ft-overlay{ position: fixed; inset: 0; background: rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; z-index: 200000; }
.ft-embed{ position: relative; background: transparent; display:flex; align-items:stretch; justify-content:stretch; width:100%; height:100%; flex:1; }
.ft-dialog{ position:relative; width: 1000px; height: 640px; background: #fff; color:#0f172a; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,.25); display:flex; flex-direction:column; overflow:hidden; }
.ft-dialog.embed{ width:100%; height:100%; border-radius:0; box-shadow:none; }
.ft-header{ display:flex; align-items:center; justify-content:space-between; padding:10px 12px; border-bottom:1px solid #e5e7eb; background:linear-gradient(180deg,#f6f8ff,#eef2ff); }
.ft-title{ font-weight:600; color:#0b57d0; }
.ft-actions{ display:flex; align-items:center; gap:8px; }
.ft-header .icon-btn.back{ width:28px; height:28px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; }
.ft-header .icon-btn.back:hover{ background:#f8fafc; }
.ft-toolbar{ display:flex; align-items:center; justify-content:space-between; gap:10px; padding:8px 12px; border-bottom:1px solid #e5e7eb; background:#fafbff; }
.ft-toolbar .hint{ color:#64748b; font-size:12px; margin-left:8px; }
.ft-toolbar .hint.path{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
.path-display{ display:inline-flex; align-items:center; gap:6px; max-width: 360px; }
.path-display{ max-width: 520px; }
.path-display .path{ display:inline-block; max-width: 480px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.icon-btn.sm{ width:24px; height:24px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; }
.icon-btn.sm:hover{ background:#f8fafc; }
.ft-body{ flex:1; display:flex; min-height:0; column-gap:0; align-items:stretch; }
/* 让左右面板使用自定义宽度 */
.ft-body .pane{ flex:0 0 auto; display:flex; flex-direction:column; min-width:0; border-right:2px solid #cbd5e1; }
.ft-body .pane:last-child{ border-right:none; }
/* 垂直分隔条 */
.v-split{ flex: 0 0 4px; cursor: ew-resize; background: linear-gradient(180deg,#e5e7eb,#cbd5e1); }
.v-split:hover{ background: linear-gradient(180deg,#dbe2ea,#b7c3d0); }
.pane:last-child{ border-right:none; }
.tree{ flex:1; display:flex; flex-direction:column; padding:8px 12px; min-height:0; overflow:hidden; }
.pane.left .tree{ padding-right:5px; }
.pane.right .tree{ padding-left:5px; }
.pane-title{ font-weight:600; color:#0b57d0; margin:4px 0; font-size:13px; display:flex; align-items:center; gap:6px; }
.pane.left .pane-title{ padding-right:5px; }
.pane.right .pane-title{ padding-left:5px; }
.pane.left .pane-title::before{ content:'💻'; }
.pane.right .pane-title::before{ content:'🖥️'; }
.pathbar{ display:flex; align-items:center; gap:8px; padding:6px 0; }
/* 靠近左右分隔线的额外留白 */
.pane.left .pathbar{ padding-right:5px; }
.pane.right .pathbar{ padding-left:5px; }
/* 统一路径工具栏高度与样式，确保左右输入框对齐 */
.pathbar .btn{ height:30px; padding:0 10px; line-height:28px; }
.pathbar .path-input{ height:30px; line-height:30px; padding:0 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:13px; }
/* 按钮组：恢复组内无额外间隙，仅保持与输入框的全局 gap */
.pathbar .btn-group{ display:inline-flex; gap:0; }
.pathbar .btn-group .icon-btn{ border-radius:6px; }
/* 旧规则：仅当路径栏在可滚动容器内时才需要粘性，这里路径栏已移出滚动区域，关闭该效果 */
/* .tree .pathbar{ position: sticky; top:0; background:#fff; z-index:5; padding-top:8px; } */
.list-wrap{ flex:1; min-height:0; overflow-y:auto; overflow-x:hidden; }
.ft-table{ width:100%; border-collapse:collapse; }
.list-wrap .ft-table thead th{ position: sticky; top: 0; z-index: 2; background: #fff; }
.ft-table thead th{ text-align:left; font-weight:600; color:#475569; padding:6px 10px; border-bottom:1px solid #e5e7eb; font-size:13px; }
.ft-table tbody td{ padding:6px 10px; border-bottom:1px solid #eef2f7; font-size:13px; color:#0f172a; }
.ft-table tbody tr:hover{ background:#f8fafc; }
.ft-table tbody tr.selected{ background:#e6f0ff; }
.ft-table .col-name{ width: 56%; }
.ft-table .col-size{ width: 14%; text-align:right; color:#475569; }
.ft-table .col-time{ width: 30%; color:#475569; }
.ft-table .icon{ display:inline-flex; width:14px; height:14px; margin-right:6px; }
.icon.directory::before{ content:'📁'; }
.icon.file::before{ content:'📄'; }
.name{ cursor:pointer; }
.empty{ padding:20px; color:#94a3b8; font-size:12px; }
.ft-footer{ padding:6px 12px; border-top:1px solid #e5e7eb; background:#f8fafc; display:flex; flex-direction: column; align-items:stretch; gap:6px; height: 100px; box-sizing: border-box; overflow: hidden; }
.ft-toolbar{ flex:0 0 auto; display:flex; align-items:center; gap:12px; }
.ft-tabs{ flex:0 0 auto; }
.status{ margin-left:auto; flex:0 0 320px; max-width: 40%; text-align:right; color:#64748b; font-size:12px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.transfers{ flex:1; min-width:0; min-height:0; overflow-y:auto; overflow-x:hidden; }
.transfers .tx-table{ width:100%; border-collapse: collapse; font-size:12px; table-layout: fixed; }
.transfers .tx-table th, .transfers .tx-table td{ padding:4px 6px; border-bottom:1px solid #e5e7eb; white-space: nowrap; }
.transfers .tx-table td.tx-prog{ width: 28%; }
.transfers .tx-table td.tx-name{ width: 36%; }
.transfers .tx-table td.tx-dir{ width: 8%; }
.transfers .tx-table td.tx-pct{ width: 8%; }
.transfers .tx-table td.tx-speed{ width: 10%; }
.transfers .tx-table td.tx-eta{ width: 8%; }
.transfers .tx-table td.tx-status{ width: 8%; }
.transfers .tx-table th{ text-align:left; color:#64748b; font-weight:600; }
.tx-name{ max-width:320px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.tx-bar{ width:100%; height:8px; background:#e5e7eb; border-radius:4px; overflow:hidden; }
.tx-bar > i{ display:block; height:100%; background:#60a5fa; width:0; }
.btn{ height:28px; padding:0 10px; border:1px solid #cbd5e1; border-radius:6px; background:#ffffff; color:#334155; cursor:pointer; }
.btn:hover{ background:#f8fafc; }
.pathbar{ display:flex; align-items:center; gap:8px; padding:6px 0; }
.path-input{ flex:1; min-width:0; height:30px; line-height:30px; border:1px solid #cbd5e1; border-radius:6px; padding:0 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; box-sizing:border-box; }
.path-input.current{ flex: 1.2; background:#f8fafc; }
.btn{ height:30px; line-height:28px; box-sizing:border-box; }
</style>
