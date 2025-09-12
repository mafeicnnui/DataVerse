<template>
  <div class="console-window" :class="{ collapsed }">
    <aside class="sidebar">
      <div class="side-header">
        <span class="title">主机</span>
      </div>
      <div class="side-body">
        <div class="search">
          <span class="icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </span>
          <input v-model.trim="kw" placeholder="搜索描述/地址/端口" @keyup.enter="" />
        </div>
        <!-- 主机类型分组列表（始终优先显示分组） -->
        <div class="group-list">
          <div v-for="g in hostGroups" :key="g.key" class="group">
            <div class="group-header" @click="toggleGroup(g.key)" :title="`展开/收起 ${g.label}`">
              <span class="caret" :class="{ open: groupOpen[g.key] }" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </span>
              <span class="gicon" aria-hidden="true">
                <!-- Windows 图标 -->
                <svg v-if="g.key==='windows'" viewBox="0 0 24 24" width="16" height="16" fill="#0b57d0"><path d="M2 4l9-1.5v9L2 11V4zm0 9l9 .5v9L2 20v-7zm11-10L22 2v9l-9 .5V3zm0 11L22 14v8l-9-1.5V14z"/></svg>
                <!-- Linux 图标（简化） -->
                <svg v-else-if="g.key==='linux'" viewBox="0 0 24 24" width="16" height="16" fill="#16a34a"><path d="M12 2c2.5 0 4 1.8 4 4 0 1.6-.8 2.8-1.6 4 .8.7 1.6 1.8 1.6 3.5 0 3-2.2 6.5-4 6.5s-4-3.5-4-6.5c0-1.7.8-2.8 1.6-3.5C8.8 8.8 8 7.6 8 6c0-2.2 1.5-4 4-4z"/></svg>
                <!-- macOS 图标（简化 Apple 叶子） -->
                <svg v-else-if="g.key==='macos'" viewBox="0 0 24 24" width="16" height="16" fill="#111827"><path d="M16.5 2c-.8.5-1.5 1.3-1.9 2.2-.5 1-.8 2.1-.6 3.2 1.1.1 2.2-.3 3.1-1 .8-.6 1.4-1.5 1.8-2.5-.9-.5-1.6-1-2.4-1.9zM12 7c-1.6 0-3 .9-3.8 2.3-.8 1.3-1.1 3-.6 4.5.5 1.8 2 3.7 3.8 3.7s2.1-1.2 3.9-1.2 2.3 1.2 3.9 1.2c1.8 0 3.2-1.9 3.8-3.7.3-.8.4-1.5.4-2.3-2.2-.1-4.1-1.3-5.1-3-1.2-1.9-1.6-4.5-.3-6.5C16.2 2.3 15 2 13.9 2 12.7 2 11.6 2.4 10.7 3.1 9.8 3.8 9.1 4.8 8.8 6c.9.6 2 .9 3.2 1z"/></svg>
                <!-- 其它（兜底） -->
                <svg v-else viewBox="0 0 24 24" width="16" height="16" fill="#64748b"><path d="M4 5h16v12H4z"/><path d="M2 19h20v2H2z"/></svg>
              </span>
              <span class="gname">{{ g.label }}</span>
            </div>
            <ul class="tree" v-show="groupOpen[g.key]">
              <li v-for="h in g.items" :key="h.id" @click="openHost(h)" :title="`${h.server_desc||''} (${h.server_ip}:${h.server_port})`" class="host-item">
                <span class="ip-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="#475569"><path d="M4 5h16v10H4z"/><path d="M8 19h8v2H8z"/></svg>
                </span>
                <span class="ip link">{{ h.server_ip }}</span>
                <!-- 悬停显示：FTP 图标按钮，点击打开 FTP 标签页 -->
                <button class="ftp-fab" @click.stop="openFtp(h)" title="打开 FTP 传输">
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="4" width="18" height="12" rx="2" ry="2"/>
                    <path d="M7 20h10"/>
                    <path d="M9 8h6"/>
                  </svg>
                </button>
              </li>
            </ul>
          </div>
        </div>
        <ul class="tree" v-if="hostGroups.length === 0">
          <li class="empty" style="pointer-events:none;color:#94a3b8;">暂无主机</li>
        </ul>
      </div>
    </aside>
    <!-- 全局折叠按钮：展开时位于侧栏右缘中部；折叠时位于页面最左缘中部。尺寸一致，仅图标方向变化 -->
    <button class="collapse-toggle" @click="toggleCollapse" :title="collapsed?'展开':'收起'">{{ collapsed ? '›' : '‹' }}</button>
    <main class="main">
      <div class="tabs-bar">
        <button class="tab-arrow left" v-show="showLeft" @click="scrollTabs(-160)" title="向左滚动">‹</button>
        <div class="tabs-scroll" ref="tabsScroll">
          <div class="tabs">
            <div v-for="t in tabs" :key="t.id" class="tab" :class="{ active: t.id===activeId }" @click="activeId=t.id" @contextmenu.prevent="onTabContextMenu($event, t)">
              <span class="label">{{ t.title }}</span>
              <button class="x" @click.stop="askClose(t.id)" title="关闭">×</button>
            </div>
          </div>
        </div>
        <button class="tab-arrow right" v-show="showRight" @click="scrollTabs(160)" title="向右滚动">›</button>
        <!-- 文件传输按钮（打开双栏文件管理器） -->
        <button class="tab-action ft" @click="openTransfer" title="文件传输（上传/下载）" aria-label="文件传输">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <!-- 类文件夹底板 -->
            <path d="M3 7h6l2 2h8a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z" fill="#f1f5f9" stroke="#334155"/>
            <!-- 圆环箭头（传输感） -->
            <path d="M12 11a4 4 0 1 1-3.5 6" stroke="#334155" fill="none"/>
            <polyline points="8.5 16 8.5 12.5 12 12.5" stroke="#2563eb"/>
            <path d="M12 11a4 4 0 0 1 3.5 6" stroke="#334155" fill="none"/>
            <polyline points="15.5 13 15.5 16.5 12 16.5" stroke="#10b981"/>
          </svg>
        </button>
        <!-- 复制当前标签（方案A） -->
        <button class="tab-action dup" @click="duplicateCurrentTab" title="复制当前标签">⧉</button>
        <!-- 返回上一页按钮（右上角） -->
        <button class="tab-action back" @click="askExitAll()" title="返回上一页">↩</button>
        <!-- 全局最小化控制台（放到返回按钮右侧） -->
        <button class="tab-action mini" @click="minimizeAll()" title="最小化控制台" aria-label="最小化控制台">🗕</button>
        <!-- 渐隐遮罩，提示可滚动 -->
        <div class="tabs-fade left" v-show="showLeft"></div>
        <div class="tabs-fade right" v-show="showRight"></div>
      </div>
      <div class="panes">
        <div v-for="t in tabs" :key="t.id" class="pane" v-show="t.id===activeId">
          <div class="pane-body" :class="{ ftp: t.mode==='ftp' }" :key="t.reloadToken">
            <div v-if="t.disconnected && t.mode!=='ftp'" class="banner">
              <span class="badge">已断开</span>
              <button class="btn" @click="reconnect(t)">重连</button>
            </div>
            <!-- SSH Pane -->
            <WebSSH v-if="t.mode!=='ftp'"
                    :host="t.host.server_ip" :port="Number(t.host.server_port||22)" :user="t.host.server_user||''" :pass="passwordOf(t.host)" :auth="authOf(t.host)" :privateKey="keyOf(t.host)" :keyPass="keyPassOf(t.host)" :tabId="t.id" />
            <!-- FTP Pane（嵌入文件传输窗口） -->
            <div v-else class="ftp-wrap">
              <FileTransferDialog :embedded="true" :visible="true" :hostInfo="{ host: String(t.host.server_ip||''), port: Number(t.host.server_port||22), user: String(t.host.server_user||''), auth: authOf(t.host), pass: passwordOf(t.host), privateKey: keyOf(t.host), keyPass: keyPassOf(t.host) }" @close="closeTab(t.id)" />
            </div>
          </div>
        </div>
        <div v-if="!tabs.length" class="empty">双击左侧主机或点击“打开”创建会话</div>
      </div>
    </main>

    <!-- 标签右键菜单（方案B） -->
    <div v-if="ctx.visible" class="ctxmenu" :style="{left: ctx.x + 'px', top: ctx.y + 'px'}" @click.stop>
      <div class="item" @click="duplicateTabById(ctx.tabId)">复制标签</div>
      <div class="item danger" @click="askClose(ctx.tabId)">关闭标签</div>
    </div>

    <!-- 返回上一页确认弹窗 -->
    <div v-if="confirmExitVisible" class="overlay" @click.self="cancelExitAll()">
      <div class="dialog">
        <div class="dialog-title">确认返回</div>
        <div class="dialog-body">返回上一页将关闭当前页面，所有 WebSSH 连接会断开。确定要返回上一页吗？</div>
        <div class="dialog-actions">
          <button class="btn" @click="cancelExitAll()">取消</button>
          <button class="btn primary" @click="confirmExitAll()">确定</button>
        </div>
      </div>
    </div>

    <!-- 关闭标签页确认弹窗（自定义样式） -->
    <div v-if="confirmCloseVisible" class="overlay" @click.self="cancelClose()">
      <div class="dialog">
        <div class="dialog-title">确认关闭</div>
        <div class="dialog-body">确定要关闭该 WebSSH 标签页吗？未保存的操作将会丢失。</div>
        <div class="dialog-actions">
          <button class="btn" @click="cancelClose()">取消</button>
          <button class="btn primary" @click="confirmClose()">确定</button>
        </div>
      </div>
    </div>

    <!-- 文件传输弹窗（保留现有入口），FTP 模式使用嵌入式，不走此处弹窗 -->
    <FileTransferDialog :visible="transferVisible" :hostInfo="currentHostInfo" @close="transferVisible=false" />

    

    <!-- 右下角最小化气泡：显示已最小化的 SSH 会话，点击恢复 -->
    <div class="mini-dock">
      <div v-for="(t,idx) in tabs.filter(x=>x.mode!=='ftp' && x.minimized)" :key="t.id" class="mini-bubble" :style="{ bottom: (16 + idx*58) + 'px' }" @click="restoreTab(t)">
        <span class="icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="12" rx="2" ry="2"/>
            <path d="M7 20h10"/>
          </svg>
        </span>
        <span class="text">{{ t.title }}</span>
        <span class="restore">点击还原</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { watch } from 'vue'
import { onMounted, onBeforeUnmount, ref, reactive, computed, nextTick } from 'vue'
import api from '../../api'
import FileTransferDialog from './FileTransferDialog.vue'
import WebSSH from './WebSSH.vue'

const hosts = ref([])
const kw = ref('')
const collapsed = ref(false)
const tabs = reactive([]) // {id, title, host, disconnected?:boolean, reloadToken?:string}

// 打开 FTP 标签页：标题 IP-FTP-N（按该 IP 现有 FTP 标签计数）
function openFtp(h){
  try{
    const sameHost = tabs.filter(t => (t?.host?.server_ip===h.server_ip && String(t?.host?.server_port||'')===String(h.server_port||'')) && t.mode==='ftp')
    const seq = sameHost.length + 1
    const id = `${h.server_ip}:${h.server_port}#ftp#${Date.now()}`
    const title = `${h.server_ip}-FTP-${seq}`
    const tab = { id, title, host: h, mode: 'ftp', disconnected: false, reloadToken: `${Date.now()}:${Math.random()}` }
    tabs.push(tab)
    activeId.value = id
  }catch{}
}
const counters = reactive({}) // per-server counters
const activeId = ref('')
// 当激活的标签变化时，向窗口广播事件，便于子组件感知重新激活
watch(activeId, (id) => {
  try { window.dispatchEvent(new CustomEvent('tab-activated', { detail: { tabId: id } })) } catch {}
})
const confirmCloseVisible = ref(false)
const pendingCloseId = ref('')
const tabsScroll = ref(null)

// 还原：从 localStorage 恢复上次最小化前的标签快照
function restoreTabsFromStorage(){
  try{
    const raw = localStorage.getItem('dv_console_restore')
    if (!raw) return
    localStorage.removeItem('dv_console_restore')
    const data = JSON.parse(raw)
    if (!data || !Array.isArray(data.tabs)) return
    // 清空现有 tabs 并恢复
    try { tabs.splice(0, tabs.length) } catch {}
    for (const t of data.tabs){
      const id = t.id || `${t?.host?.server_ip||'host'}:${t?.host?.server_port||''}#${t.mode||'ssh'}#${Date.now()}`
      const title = t.title || `${t?.host?.server_ip||''}-${(t.mode||'SSH').toUpperCase()}`
      tabs.push({ id, title, host: t.host, mode: t.mode||'ssh', disconnected: false, reloadToken: `${Date.now()}:${Math.random()}` })
    }
    if (data.activeId){ activeId.value = data.activeId }
  }catch{}
}
onMounted(()=>{ 
  try{ if (!window.name) window.name = 'dv_console' }catch{}
  try{ restoreTabsFromStorage() }catch{}
  // 心跳：定期写入 localStorage，供父页面判断窗口是否仍存活
  try{
    const beat = () => { try { localStorage.setItem('dv_console_alive', String(Date.now())) } catch {} }
    beat(); const timer = setInterval(beat, 2000)
    window.addEventListener('beforeunload', ()=>{ try { clearInterval(timer) } catch {} })
  }catch{}
  // 监听父页面发来的还原指令
  try{
    window.addEventListener('message', (ev)=>{
      const data = ev?.data || {}
      if (data && data.type==='console-restore'){
        try{ window.focus() }catch{}
      }
    })
  }catch{}
  // BroadcastChannel 方式接收还原指令并回执
  try{
    const ch = new BroadcastChannel('dv_console')
    ch.onmessage = (ev)=>{
      const data = ev?.data || {}
      if (data && data.type==='restore'){
        try{ window.focus() }catch{}
        try{ ch.postMessage({ type: 'restore-ack', ts: Date.now() }) }catch{}
      }
    }
    window.addEventListener('beforeunload', ()=>{ try { ch.close() } catch {} })
  }catch{}
})
const showLeft = ref(false)
const showRight = ref(false)
// 右键菜单状态
const ctx = reactive({ visible: false, x: 0, y: 0, tabId: '' })
// 返回确认弹窗
const confirmExitVisible = ref(false)
// 文件传输对话框
const transferVisible = ref(false)
const currentHostInfo = computed(() => {
  const t = tabs.find(x => x.id === activeId.value)
  const h = t?.host || {}
  return {
    host: String(h.server_ip||''),
    port: Number(h.server_port||22),
    user: String(h.server_user||''),
    auth: authOf(h),
    pass: passwordOf(h),
    privateKey: keyOf(h),
    keyPass: keyPassOf(h),
  }
})
function openTransfer(){ transferVisible.value = true }

// 基于 hosts 与 kw 的本地过滤，避免依赖外部变量的初始化顺序
function localFilteredHosts(){
  const list = Array.isArray(hosts?.value) ? hosts.value : []
  const q = (kw?.value || '').toString().trim().toLowerCase()
  if (!q) return list
  return list.filter(h => {
    const desc = (h.server_desc ?? '').toString().toLowerCase()
    const ip = (h.server_ip ?? '').toString().toLowerCase()
    const port = (h.server_port ?? '').toString()
    return desc.includes(q) || ip.includes(q) || port.includes(q)
  })
}

// 统一系统类型映射：支持字典码与字符串
// 需求：下拉框存的是代码，数据库 server_os 存的是数字或数字字符串，如 1/2/3
// 约定：1=windows, 2=linux, 3=macOS
function normalizeOS(h){
  const v = h?.system ?? h?.server_os ?? h?.os ?? ''
  const s = String(v).trim().toLowerCase()
  if (!s) return ''
  if (s === '1') return 'windows'
  if (s === '2') return 'linux'
  if (s === '3') return 'macos'
  if (s.startsWith('win')) return 'windows'
  if (s.includes('linux')) return 'linux'
  if (s.includes('mac') || s.includes('darwin') || s.includes('os x')) return 'macos'
  return ''
}

// 当前系统类型列表（接口给到视图使用）：依据“主机录入项中的系统”字段，统一映射为 windows/linux/macos
const systemTypes = computed(() => {
  const list = localFilteredHosts()
  const set = new Set()
  for (const h of list) {
    const key = normalizeOS(h)
    if (key) set.add(key)
  }
  // 固定顺序输出
  const order = ['windows', 'linux', 'macos']
  return order.filter(k => set.has(k))
})

// 主机类型分组：仅对当前存在的系统类型分组（不显示其它类型）
const hostGroups = computed(() => {
  const list = localFilteredHosts()
  const buckets = { windows: [], linux: [], macos: [] }
  for (const h of list) {
    const key = normalizeOS(h)
    if (key && buckets[key]) buckets[key].push(h)
  }
  const meta = [
    { key: 'windows', label: 'Windows' },
    { key: 'linux', label: 'Linux' },
    { key: 'macos', label: 'macOS' },
  ]
  return meta
    .filter(m => systemTypes.value.includes(m.key))
    .map(m => ({ key: m.key, label: m.label, items: buckets[m.key] }))
})

// 分组展开状态：默认全部收起，仅在有“当前主机分组”时展开对应组
const groupOpen = reactive({})
const currentGroupKey = ref('')

function setGroupOpenByKey(key){
  // 先将所有已存在的键设为收起
  for (const k of Object.keys(groupOpen)) {
    groupOpen[k] = false
  }
  // 仅展开传入键（若存在于当前分组）
  if (key && hostGroups.value.some(g => g.key === key)) {
    groupOpen[key] = true
  }
}

function focusGroupByHost(h){
  const key = normalizeOS(h)
  currentGroupKey.value = key
  setGroupOpenByKey(key)
}

watch(hostGroups, (gs) => {
  const keys = new Set(gs.map(g => g.key))
  // 移除不存在的键
  for (const k of Object.keys(groupOpen)) { if (!keys.has(k)) delete groupOpen[k] }
  // 新增默认值为收起
  for (const k of keys) { if (!(k in groupOpen)) groupOpen[k] = false }
  // 若已有当前分组键，则仅展开该分组
  if (currentGroupKey.value) {
    setGroupOpenByKey(currentGroupKey.value)
  }
}, { immediate: true })

function toggleGroup(key){ groupOpen[key] = !groupOpen[key] }

// 监听会话退出，标记对应 tab 为断开（放在顶层，确保生命周期可正确注册/注销）
const onExit = (e) => {
  try {
    const tabId = e?.detail?.tabId || activeId.value
    const t = tabs.find(i => i.id === tabId)
    if (t) {
      t.disconnected = true
    }
  } catch {}
}

function toggleCollapse(){ collapsed.value = !collapsed.value }

const filteredHosts = computed(() => {
  const k = (kw.value||'').toLowerCase()
  if (!k) return hosts.value
  return (hosts.value||[]).filter(h => `${h.server_desc||''} ${h.server_ip||''} ${h.server_port||''}`.toLowerCase().includes(k))
})

function authIsKey(val){
  const v = (val||'').toLowerCase()
  if (v==='key') return true
  return v.includes('key') || v.includes('密钥')
}
function authIsPassword(val){ return !authIsKey(val) }
function authOf(h){ return authIsKey(h.auth_memthod)?'key':'password' }
function passwordOf(h){ return authIsPassword(h.auth_memthod) ? (h.server_pass||'') : '' }
function keyOf(h){ return authIsKey(h.auth_memthod) ? (h.private_key||'') : '' }
function keyPassOf(h){ return authIsKey(h.auth_memthod) ? (h.key_passphrase||'') : '' }

function openHost(h){
  const serverKey = String(h.id || `${h.server_ip}:${h.server_port}`)
  const seq = (counters[serverKey] = (counters[serverKey] || 0) + 1)
  const uid = `${serverKey}#${Date.now()}#${Math.random().toString(36).slice(2,8)}`
  const title = `${h.server_ip}-${seq}`
  const tab = { id: uid, title, host: h, disconnected: false, reloadToken: `${Date.now()}:${Math.random()}`, minimized: false }
  tabs.push(tab)
  activeId.value = uid
}
// 向父组件暴露“添加标签”能力，便于 App.vue 以悬浮窗方式打开控制台
defineExpose({ addTab: openHost })
function askClose(id){
  pendingCloseId.value = id
  confirmCloseVisible.value = true
}
function confirmClose(){
  const id = pendingCloseId.value
  const idx = tabs.findIndex(t => t.id===id)
  if (idx>=0){
    // 记录待关闭标签的主机键，用于稍后判断是否需要重置序号
    const t = tabs[idx]
    const h = t?.host || {}
    const serverKey = String(h.id || `${h.server_ip}:${h.server_port}`)
    tabs.splice(idx,1)
    if (activeId.value===id){
      activeId.value = tabs[idx]?.id || tabs[idx-1]?.id || ''
    }
    // 若所有标签均已关闭，则清空所有计数器
    if (tabs.length === 0) {
      try { Object.keys(counters).forEach(k => delete counters[k]) } catch {}
    }
    // 若该主机的所有标签均已关闭，则重置其计数器，使下次从 1 开始
    try {
      const stillHas = tabs.some(x => {
        const hx = x?.host || {}
        const keyx = String(hx.id || `${hx.server_ip}:${hx.server_port}`)
        return keyx === serverKey
      })
      if (!stillHas && serverKey) {
        delete counters[serverKey]
      }
    } catch {}
  }
  confirmCloseVisible.value = false
  pendingCloseId.value = ''
}
function cancelClose(){
  confirmCloseVisible.value = false
  pendingCloseId.value = ''
}

// 全局最小化/还原
function minimizeAll(){
  try {
    // 若作为悬浮模态在当前页面展示，则直接通知父页面隐藏浮层并显示右下角气泡
    if (!window.opener) {
      try { window.dispatchEvent(new CustomEvent('console-minimized', { detail: { tabs: tabs.length, title: document.title||'控制台' } })) } catch {}
      return
    }
    if (window.opener && !window.opener.closed) {
      // 轻量快照（避免对象过大）：仅保留 id、title、mode、host
      const snapshot = {
        tabs: tabs.map(t => ({ id: t.id, title: t.title, mode: t.mode, host: t.host })),
        activeId: activeId.value,
        ts: Date.now(),
      }
      try { localStorage.setItem('dv_console_restore', JSON.stringify(snapshot)) } catch {}
      // 通知父页面并“伪最小化”：仅失焦，不关闭/不移动/不缩放，保持会话
      try { window.opener.postMessage({ type: 'console-minimized', tabs: tabs.length, url: location.href, title: document.title }, '*') } catch {}
      try{ window.blur() }catch{}
      return
    }
  } catch {}
  // 兜底：若无父窗口，则尝试返回历史或跳转首页
  try {
    // 同窗口：写入两个键，主页面用于显示气泡，控制台新窗口用于恢复标签
    const payload = { type: 'console-minimized', url: location.href, title: document.title, tabs: tabs.length, ts: Date.now() }
    localStorage.setItem('dv_console_bubble', JSON.stringify(payload))
    const snapshot = {
      tabs: tabs.map(t => ({ id: t.id, title: t.title, mode: t.mode, host: t.host })),
      activeId: activeId.value,
      ts: Date.now(),
    }
    localStorage.setItem('dv_console_restore', JSON.stringify(snapshot))
    // 同窗口场景不处理窗口尺寸
  } catch {}
  try { if (window.history && window.history.length > 1) { window.history.back(); return } } catch {}
  try { location.href = '/' } catch {}
}

// 最小化/还原逻辑
function minimizeTab(t){
  if (!t) return
  t.minimized = true
}
function restoreTab(t){
  if (!t) return
  t.minimized = false
  // 还原时激活该标签
  try { activeId.value = t.id } catch {}
}

onMounted(async () => {
  // 复制父窗口样式到新窗口（当前组件运行在新窗口文档中，样式需完整）
  try {
    const parentHead = window.opener?.document?.head
    const head = document.head
    if (parentHead && head){
      parentHead.querySelectorAll('style,link[rel="stylesheet"]').forEach(node => {
        try {
          if (node.tagName.toLowerCase()==='style'){
            const s = document.createElement('style')
            s.textContent = node.textContent
            head.appendChild(s)
          } else if (node.tagName.toLowerCase()==='link'){
            const l = document.createElement('link')
            l.rel = 'stylesheet'
            l.href = node.href
            head.appendChild(l)
          }
        } catch {}
      })
    }
  } catch {}

  try{
    const { data } = await api.get('/servers/')
    hosts.value = Array.isArray(data)?data:[]
  }catch(e){
    // 简单显示错误
    document.title = '控制台(加载失败)'
  }

  // 暴露给父窗口用于添加 tab
  window.addTab = (host) => openHost(host)

  // 注册监听
  window.addEventListener('webssh-exit', onExit)
  // 点击空白处关闭右键菜单
  window.addEventListener('click', () => ctx.visible = false)
  // Esc 关闭右键菜单
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape') ctx.visible = false })

  // 若通过 URL 带入主机参数，则默认打开一个会话（支持从主机管理跳转默认打开）
  try {
    const sp = new URLSearchParams(location.search)
    const hip = sp.get('h')
    const hport = sp.get('p')
    const huser = sp.get('u')
    const hauth = sp.get('a') // password | key
    const hpass = sp.get('pw')
    const hkeyb64 = sp.get('kb64')
    const hkeypass = sp.get('kpw')
    if (hip) {
      // 先在已加载的主机列表中查找对应主机，以便只展开其所在分组
      try {
        const list = Array.isArray(hosts?.value) ? hosts.value : []
        const match = list.find(x => String(x?.server_ip||'') === String(hip) && (!hport || String(x?.server_port||'') === String(hport)))
        if (match) {
          focusGroupByHost(match)
        }
      } catch {}

      const host = {
        server_ip: hip,
        server_port: hport || '22',
        server_user: huser || '',
        auth_memthod: hauth || 'password',
        server_pass: hpass || '',
        private_key: hkeyb64 ? atob(hkeyb64) : '',
        key_passphrase: hkeypass || '',
      }
      openHost(host)
    }
  } catch {}
})

// 卸载时清理监听
onBeforeUnmount(() => {
  try { window.removeEventListener('webssh-exit', onExit) } catch {}
  try { window.removeEventListener('click', () => ctx.visible = false) } catch {}
})

function reconnect(t){
  // 重置状态并强制重挂载子组件，实现“新会话”
  t.disconnected = false
  t.reloadToken = `${Date.now()}:${Math.random()}`
}

function scrollTabs(delta){
  const el = tabsScroll.value
  if (el) {
    el.scrollBy({ left: delta, behavior: 'smooth' })
    // 尽快刷新箭头状态，避免平滑滚动期间视觉延迟
    updateArrowVisible()
  }
}

function updateArrowVisible(){
  const el = tabsScroll.value
  if (!el) return
  const content = el.querySelector('.tabs')
  const contentWidth = content ? content.scrollWidth : el.scrollWidth
  const maxScrollLeft = Math.max(0, contentWidth - el.clientWidth)
  const left = el.scrollLeft
  const canScroll = contentWidth > el.clientWidth + 1
  showLeft.value = canScroll && left > 1
  showRight.value = canScroll && left <= (maxScrollLeft - 0.5)
}

let ro
let wheelHandler = null
onMounted(() => {
  const el = tabsScroll.value
  if (!el) return
  el.addEventListener('scroll', updateArrowVisible, { passive: true })
  // 鼠标滚轮纵向转横向，提升可用性
  wheelHandler = (e) => {
    if (!el) return
    const dx = Math.abs(e.deltaX)
    const dy = Math.abs(e.deltaY)
    // 以纵向为主来驱动横向滚动
    const delta = dy > dx ? e.deltaY : e.deltaX
    if (delta !== 0) {
      e.preventDefault()
      el.scrollLeft += delta
      updateArrowVisible()
    }
  }
  el.addEventListener('wheel', wheelHandler, { passive: false })
  // 监听尺寸变化
  try {
    ro = new ResizeObserver(updateArrowVisible)
    ro.observe(el)
  } catch {
    window.addEventListener('resize', updateArrowVisible)
  }
  // 初始计算
  nextTick(() => { updateArrowVisible(); scrollActiveIntoView(false) })
})

onBeforeUnmount(() => {
  const el = tabsScroll.value
  if (el) {
    el.removeEventListener('scroll', updateArrowVisible)
    if (wheelHandler) el.removeEventListener('wheel', wheelHandler)
  }
  if (ro) {
    try { ro.disconnect() } catch {}
  } else {
    window.removeEventListener('resize', updateArrowVisible)
  }
})

// 当 tabs 变化或激活变更时，重新计算可滚动性
watch(
  () => [tabs.length, activeId.value],
  () => nextTick(() => { updateArrowVisible(); scrollActiveIntoView(true) })
)

function scrollActiveIntoView(smooth = true){
  const el = tabsScroll.value
  if (!el) return
  const active = el.querySelector('.tab.active')
  if (active && typeof active.scrollIntoView === 'function') {
    try {
      active.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', inline: 'nearest', block: 'nearest' })
    } catch {}
  }
}

// ========== 复制标签逻辑 ==========
function onTabContextMenu(ev, t){
  ev.preventDefault()
  ctx.visible = true
  // 防止超出窗口，留出菜单宽高预估
  const menuW = 140, menuH = 80
  const vw = window.innerWidth, vh = window.innerHeight
  ctx.x = Math.min(ev.clientX, vw - menuW - 4)
  ctx.y = Math.min(ev.clientY, vh - menuH - 4)
  ctx.tabId = t?.id || ''
}

function duplicateCurrentTab(){
  const t = tabs.find(x => x.id === activeId.value)
  if (t) duplicateTabById(t.id)
}

function duplicateTabById(id){
  const t = tabs.find(x => x.id === id)
  if (!t) return
  // 克隆 host 参数，走 openHost 生成新会话与标题
  const h = { ...t.host }
  openHost(h)
  nextTick(() => { scrollActiveIntoView(true) })
  ctx.visible = false
}

// ========== 返回上一页 ==========
function askExitAll(){
  confirmExitVisible.value = true
}
function cancelExitAll(){ confirmExitVisible.value = false }
function confirmExitAll(){
  confirmExitVisible.value = false
  // 优先：如果是脚本打开的独立窗口，聚焦父窗口并直接关闭当前窗口
  try {
    if (window.opener && !window.opener.closed) {
      try { window.opener.focus() } catch {}
      window.close()
      return
    }
  } catch {}
  // 其次：有历史记录则后退
  try {
    if (window.history && window.history.length > 1) {
      window.history.back()
      return
    }
  } catch {}
  // 兜底：跳转到站点根（可按需改为控制台列表页）
  try { location.href = '/' } catch {}
}
</script>

<style scoped>
/* 顶部误放的样式已移除，统一放在此处 */
/* 悬浮显示 FTP 快捷按钮 */
.ftp-fab{ margin-left:6px; border:1px solid #cbd5e1; border-radius:6px; background:#fff; color:#334155; width:22px; height:22px; display:inline-flex; align-items:center; justify-content:center; opacity:0; pointer-events:none; transition:opacity .12s ease; }
.host-item:hover .ftp-fab{ opacity:1; pointer-events:auto; }
html, body, #app { height: 100%; }
.console-window { display: flex; height: 100vh; width: 100vw; overflow: hidden; background: #ffffff; color: #0f172a; }
/* 使容器作为定位上下文 */
.console-window { position: relative; }
/* 菜单区（侧栏）改为与系统主菜单一致的浅色系 */
.sidebar { width: 230px; flex: 0 0 230px; background: #ffffff; border-right: 1px solid #e5e7eb; display: flex; flex-direction: column; color: #0f172a; transition: width .2s ease, flex-basis .2s ease; position: relative; box-sizing: border-box; overflow: visible; }
.console-window.collapsed .sidebar { width: 0 !important; min-width: 0 !important; flex: 0 0 0 !important; border-right: 0 !important; }
.side-header { display: flex; align-items: center; justify-content: space-between; padding: 8px 10px; color: #0b57d0; border-bottom: 1px solid #e5e7eb; background: #f5f7ff; height: 44px; box-sizing: border-box; }
.title { font-weight: 600; }
.collapse-btn { width: 28px; height: 28px; border: 1px solid #d1d5db; border-radius: 6px; background: #ffffff; color: #475569; cursor: pointer; }
.collapse-toggle { position: absolute; top: 50%; transform: translateY(-50%); left: calc(230px - 10px); width: 18px; height: 26px; font-size: 12px; font-weight: 600; border: 1px solid #d1d5db; border-left: none; border-radius: 0 6px 6px 0; background: #ffffff; color: #475569; box-shadow: 0 2px 8px rgba(0,0,0,0.12); display: inline-flex; align-items: center; justify-content: center; z-index: 20; padding: 0; cursor: pointer; }
.console-window.collapsed .collapse-toggle { left: 0; border-left: none; border-right: 1px solid #d1d5db; border-radius: 6px 0 0 6px; }
.console-window.collapsed .side-header { display: none !important; }
.console-window.collapsed .side-header .title { display: none !important; }
.side-body { flex: 1; overflow: auto; padding: 8px; }
.console-window.collapsed .side-body { display: none !important; }
.search { position: relative; }
.search .icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #94a3b8; display: inline-flex; align-items: center; }
.search input { width: 100%; height: 30px; border: 1px solid #e5e7eb; border-radius: 6px; padding: 0 8px 0 34px; background: #ffffff; color: #0f172a; }
.tree { margin: 8px 0 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 6px; }
/* 压缩组头高度与内边距，使整体更紧凑 */
.group-header { padding: 6px 10px; min-height: 28px; }
/* 组图标与名称更贴近，减少占位 */
.group-header .gicon { width: 16px; height: 16px; margin-right: 6px; }
/* 一级菜单字体：取消粗体，字号减 1 */
.group-header .gname { font-weight: 400; font-size: 11px; }
/* 侧栏宽度 220px，提供可调缩进变量（可按需微调） */
.sidebar { flex: 0 0 230px; width: 230px; flex-shrink: 0; --tree-indent: 28px; }
/* 折叠按钮定位到主机菜单右边框中部 */
.collapse-toggle { position: absolute; left: 230px; top: 50%; transform: translate(-50%, -50%); width: 18px; height: 26px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; color: #334155; z-index: 15000; box-shadow: 0 2px 6px rgba(0,0,0,.08); display: flex; align-items: center; justify-content: center; padding: 0; box-sizing: border-box; overflow: hidden; }
/* 折叠与展开状态保持完全一致的尺寸与内边距 */
.console-window.collapsed .collapse-toggle { left: 0; transform: translate(0, -50%); width: 18px; height: 26px; padding: 0; }
/* 标准化内部图标大小，避免字符宽度引起的视觉差异 */
.collapse-toggle > svg, .collapse-toggle > i, .collapse-toggle > span { width: 12px; height: 12px; font-size: 12px; line-height: 1; display: inline-block; }
.main { flex: 1 1 auto; display: flex; flex-direction: column; min-width: 0; min-height: 0; background:#ffffff; }
.panes { flex: 1; position: relative; min-height: 0; background:#ffffff; }

/* 二级菜单（IP 列表）对齐到一级图标正下方，使用变量便于微调。
   适配两种 DOM：div.items > ul.tree 或 直接 ul.tree。*/
.group .items { box-sizing: border-box; margin: 4px 0 6px 0 !important; padding-left: var(--tree-indent) !important; }
.group > .tree { box-sizing: border-box; margin: 4px 0 6px 0 !important; padding-left: var(--tree-indent) !important; }
.group .tree { margin-left: 0 !important; }
.tree { list-style: none; padding-left: 0; margin: 0; }
.group .tree li.host-item{ display:flex; align-items:center; gap:6px; height:20px; padding:0 8px; border-radius:6px; cursor:pointer; position:relative; }
.tree li:hover { background: #eef2ff; }
.ip-icon { display: inline-flex; width: 12px; height: 12px; margin-right: 6px; }
.ip.link { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-weight: 400; color: #2563eb; font-size: 12px; }
/* 强制二级菜单 IP 使用正常字重，避免被其它规则覆盖 */
.group .tree li .ip, .group .tree li .ip.link { font-weight: 400 !important; }
.pane { position: absolute; inset: 0; display: flex; flex-direction: column; }
/* Tab 标题区改为浅色，与系统主菜单一致，并加入横向滚动箭头 */
.tabs-bar { position: relative; display: flex; align-items: center; gap: 6px; padding: 6px; background: #f5f7ff; border-bottom: 1px solid #e5e7eb; min-height: 36px; }
.tabs-scroll { position: relative; flex: 1 1 auto; min-width: 0; overflow-x: auto; overflow-y: hidden; padding: 0 96px 0 44px; scrollbar-gutter: stable; z-index: 1; }
.tabs-scroll { scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent; }
.tabs-scroll::-webkit-scrollbar { height: 3px; }
.tabs-scroll::-webkit-scrollbar-track { background: transparent; }
.tabs-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 2px; }
.tabs-scroll:hover::-webkit-scrollbar-thumb { background: #a8b3c2; }
.tabs-fade { position: absolute; top: 0; height: 100%; width: 36px; pointer-events: none; z-index: 9000; }
.tabs-fade.left { left: 44px; background: linear-gradient(to right, rgba(245,247,255,1), rgba(245,247,255,0)); }
.tabs-fade.right { right: 12px; background: linear-gradient(to left, rgba(245,247,255,1), rgba(245,247,255,0)); }
.tabs { display: inline-flex; gap: 4px; white-space: nowrap; position: relative; z-index: 1; flex: 0 0 auto; }
.tab { display: inline-flex; align-items: center; gap: 6px; padding: 6px 10px; border: 1px solid #e5e7eb; border-bottom: none; border-radius: 8px 8px 0 0; background: #ffffff; color: #0f172a; cursor: pointer; font-size: 12px; white-space: nowrap; flex: 0 0 auto; }
.tab.active { background: #E6F0FF; color: #0f172a; border-color: #D6E4FF; box-shadow: inset 0 -1px 0 rgba(0,0,0,0.03); }
.tab .x { width: 18px; height: 18px; border: 1px solid #e5e7eb; border-radius: 50%; background: #ffffff; color: #64748b; cursor: pointer; }
.tab .x:hover { background: #f8fafc; color: #0f172a; }
/* 复制按钮（方案A） */
.tab-action.dup { position: absolute; right: 116px; top: 50%; transform: translateY(-50%); width: 28px; height: 28px; border: 1px solid #cbd5e1; border-radius: 6px; background: #ffffff; color: #334155; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.10); z-index: 10000; }
.tab-action.dup:hover { background: #f8fafc; }
/* 文件传输按钮 */
.tab-action.ft { position: absolute; right: 82px; top: 50%; transform: translateY(-50%); width: 28px; height: 28px; border: 1px solid #cbd5e1; border-radius: 6px; background: #ffffff; color: #334155; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.10); z-index: 10000; }
.tab-action.ft:hover { background: #f8fafc; }
/* 返回按钮（靠右第二） */
.tab-action.back { position: absolute; right: 48px; top: 50%; transform: translateY(-50%); width: 28px; height: 28px; border: 1px solid #cbd5e1; border-radius: 6px; background: #ffffff; color: #334155; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.10); z-index: 10000; }
.tab-action.back:hover { background: #f8fafc; }
/* 最小化按钮（最右侧） */
.tab-action.mini { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); width: 28px; height: 28px; border: 1px solid #cbd5e1; border-radius: 6px; background: #ffffff; color: #334155; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.10); z-index: 10000; }
.tab-action.mini:hover { background: #f8fafc; }
/* 右键菜单（方案B） */
.ctxmenu { position: fixed; min-width: 140px; background: #ffffff; color: #0f172a; border: 1px solid #e5e7eb; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); z-index: 20000; user-select: none; }
.ctxmenu .item { padding: 8px 12px; cursor: pointer; font-size: 13px; }
.ctxmenu .item:hover { background: #f1f5f9; }
.ctxmenu .item.danger { color: #ef4444; }
.ctxmenu .item.danger:hover { background: #fee2e2; }
.pane { position: absolute; inset: 0; display: flex; flex-direction: column; }
.pane-body { flex: 1; min-height: 0; background:#ffffff; }

/* FTP 模式：父容器用弹性布局撑满高度 */
.pane-body.ftp{ display:flex; }
.pane-body.ftp .ftp-wrap{ flex:1; height:100%; padding:10px; box-sizing: border-box; display:flex; min-height:0; }
/* 让嵌入的文件传输对话框占满可用高度（scoped 需使用 :deep） */
.pane-body.ftp .ftp-wrap :deep(.ft-embed){ flex:1; display:flex; min-height:0; }
.pane-body.ftp .ftp-wrap :deep(.ft-dialog.embed){ flex:1; display:flex; flex-direction:column; min-height:0; }
/* 中部主体区域可伸缩并允许滚动 */
.pane-body.ftp .ftp-wrap :deep(.ft-body){ flex:1; min-height:0; overflow:auto; }
.banner { display: flex; align-items: center; gap: 10px; padding: 8px 10px; background: #111827; border-bottom: 1px solid #1f2937; }
.badge { color: #fca5a5; background: #1f2937; border: 1px solid #374151; border-radius: 6px; padding: 2px 8px; font-size: 12px; }
.btn { height: 28px; padding: 0 10px; border: 1px solid #334155; border-radius: 6px; background: #0b1220; color: #93c5fd; cursor: pointer; }
.empty { color: #94a3b8; padding: 20px; }
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { width: 380px; border: 1px solid #1e293b; border-radius: 10px; background: #0b1220; color: #e5e7eb; box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
.dialog-title { padding: 12px 16px; border-bottom: 1px solid #1e293b; font-weight: 600; color: #93c5fd; }
.dialog-body { padding: 16px; color: #cbd5e1; }
.dialog-actions { display: flex; gap: 10px; justify-content: flex-end; padding: 12px 16px; border-top: 1px solid #1e293b; }
.dialog .btn { height: 30px; padding: 0 12px; border: 1px solid #334155; border-radius: 6px; background: #0b1220; color: #93c5fd; cursor: pointer; }
.dialog .btn.primary { background: #1d4ed8; border-color: #1d4ed8; color: #fff; }

/* ========== 优化左侧主机菜单树：连接线 + 去掉二级项边框 ========== */
/* 清除任何可能的边框/背景（确保更高优先级） */
.sidebar .group .tree li { border: none !important; background: transparent !important; }
.sidebar .group .tree .ip-icon { border: none !important; background: transparent !important; }

/* 连接线样式：从一级菜单图标正下方起笔，贯穿到二级菜单项 */
.group { position: relative; --line-x: 18px; }
.group-header{ position: relative; }
/* 从图标正下方往下延伸到列表起点 */
.group-header::after{ content:""; position:absolute; left: var(--line-x); top: 100%; bottom: -2px; border-left: 1px solid #d1d5db; }
/* 列表内继续沿同一 X 轴绘制竖线，并为每个项连一段水平线 */
.sidebar .group .tree{ position: relative; }
.sidebar .group .tree::before{ content:""; position:absolute; left: var(--line-x); top: 0; bottom: 0; border-left: 1px solid #d1d5db; }
.sidebar .group .tree li{ position: relative; margin: 1px 0; padding-top: 2px; padding-bottom: 2px; padding-left: calc(var(--line-x) + 10px); }
.sidebar .group .tree li::after{ content:""; position:absolute; left: var(--line-x); top: 10px; width: 14px; border-top: 1px solid #d1d5db; }

</style>
