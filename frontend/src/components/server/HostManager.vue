<template>
  <div class="host-mgr">
    <div class="toolbar card">
      <div class="row">
        <div class="field icon-left">
          <svg class="leading" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
          <input v-model.trim="q.keyword" class="ipt with-icon" placeholder="搜索描述 / 地址 / 端口" @keyup.enter="onQuery" aria-label="搜索" />
        </div>
        <div class="field icon-left">
          <svg class="leading" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 1 0 .001 20.001A10 10 0 0 0 12 2Zm0 3a2 2 0 1 1 0 4 2 2 0 0 1 0-4Zm0 6c2.67 0 8 1.34 8 4v3H4v-3c0-2.66 5.33-4 8-4z"/></svg>
          <select v-model="q.status" class="sel with-icon" aria-label="状态">
            <option value="">状态(全部)</option>
            <option v-for="d in dictStatus" :key="d.dmm" :value="d.dmm">{{ d.dmmc }}</option>
          </select>
        </div>
        <div class="field icon-left">
          <svg class="leading" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M3 5a2 2 0 0 1 2-2h6l2 2h6a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5zm4 4h10v2H7V9zm0 4h6v2H7v-2z"/></svg>
          <select v-model="q.os" class="sel with-icon" aria-label="系统">
            <option value="">系统(全部)</option>
            <option v-for="d in dictOS" :key="d.dmm" :value="d.dmm">{{ d.dmmc }}</option>
          </select>
        </div>
        <button class="icon-btn primary" @click="onQuery" title="查询" aria-label="查询">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
        </button>
        <button class="icon-btn primary" @click="onCreate" title="新增" aria-label="新增">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M19 11h-6V5h-2v6H5v2h6v6h2v-6h6z"/></svg>
        </button>
      </div>
    </div>

    <div class="card table-wrap">
      <table class="table cm-table">
        <colgroup>
          <col style="width:70px" />
          <col />
          <col />
          <col style="width:90px" />
          <col style="width:120px" />
          <col style="width:100px" />
          <col style="width:140px" />
          <col style="width:160px" />
        </colgroup>
        <thead>
          <tr>
            <th>标识</th>
            <th>服务器描述</th>
            <th>地址</th>
            <th>端口</th>
            <th>系统</th>
            <th>状态</th>
            <th>更新时间</th>
            <th class="op-col">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in paged" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.server_desc }}</td>
            <td>{{ item.server_ip }}</td>
            <td>{{ item.server_port }}</td>
            <td>{{ labelOf(dictOS, item.server_os) }}</td>
            <td>{{ labelOf(dictStatus, item.status) }}</td>
            <td>{{ item.update_time || '' }}</td>
            <td class="op-col">
              <button class="icon-btn sm info" @click="onEdit(item)" title="编辑" aria-label="编辑">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zm3.92.83H5v-1.92L14.06 6.02l1.92 1.92L6.92 18.08zM20.71 5.63a.996.996 0 0 0 0-1.41L19.78 3.3a.996.996 0 1 0-1.41 1.41l.93.93c.39.39 1.02.39 1.41-.01z"/></svg>
              </button>
              <button class="icon-btn sm warn" @click="onDelete(item)" title="删除" aria-label="删除">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M9 4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2h4v2H5V4h4zm2 0a0 0 0 0 0 0 0h2a0 0 0 0 0 0 0H11z"/><path d="M7 8h10v12a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2V8zm3 3v7h2v-7h-2z"/></svg>
              </button>
              <button class="icon-btn sm success" @click="onTest(item)" title="测试" aria-label="测试">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 1 0 .001 20.001A10 10 0 0 0 12 2Zm-1 14-4-4 1.41-1.41L11 12.17l5.59-5.59L18 8l-7 8z"/></svg>
              </button>
              <button class="icon-btn sm console" @click="onConsole(item)" title="控制台" aria-label="控制台">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M4 5h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Zm2 4 4 3-4 3 1.2 1.6L12 13l-4.8-3.6L6 9Zm6 7h6v-2h-6v2z"/></svg>
              </button>
            </td>
          </tr>
          <tr v-if="!filtered.length">
            <td colspan="8" class="empty">暂无数据</td>
          </tr>
        </tbody>
      </table>
      <div class="tq-pagination">
        <button class="icon-btn" @click="onPrev" :disabled="page<=1" title="上一页">‹</button>
        <span class="muted">第 {{ page }} / {{ totalPages }} 页</span>
        <input class="page-input" type="number" :min="1" :max="totalPages" :value="page" @keydown.enter.prevent="onJump($event)" style="width:84px;margin:0 6px;padding:4px 6px;border:1px solid #c7d2fe;border-radius:6px;" title="输入页码后按回车跳转" />
        <button class="icon-btn" @click="onNext" :disabled="page>=totalPages" title="下一页">›</button>
        <span class="muted" style="margin-left:8px;">每页</span>
        <select :value="pageSize" @change="onPageSizeChange">
          <option :value="20">20</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
        <span class="muted">条，共 {{ filtered.length }} 条</span>
      </div>
    </div>

    <!-- 新增/编辑 -->
    <div v-if="showModal" class="modal-backdrop" @click.stop>
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ editing ? '编辑主机' : '新增主机' }}</h2>
        </div>
        <div class="modal-body">
          <div class="grid">
            <label>
              <span>服务器描述</span>
              <input v-model.trim="form.server_desc" />
            </label>
            <label>
              <span>地址</span>
              <input v-model.trim="form.server_ip" />
            </label>
            <label>
              <span>端口</span>
              <input v-model.trim="form.server_port" />
            </label>
            <label>
              <span>认证方式</span>
              <select v-model="form.auth_memthod">
                <option v-if="!dictAuth.length" value="password">口令</option>
                <option v-if="!dictAuth.length" value="key">密钥</option>
                <option v-for="d in dictAuth" :key="d.dmm" :value="d.dmm">{{ d.dmmc }}</option>
              </select>
            </label>
            <label>
              <span>用户名</span>
              <input v-model.trim="form.server_user" />
            </label>
            <label>
              <span>口令</span>
              <input v-model.trim="form.server_pass" type="password" :disabled="isKeyValue(form.auth_memthod)" />
            </label>
            <label>
              <span>私钥</span>
              <textarea v-model="form.private_key" class="ta" :disabled="!isKeyValue(form.auth_memthod)" placeholder="PEM/OpenSSH 私钥内容，示例：-----BEGIN OPENSSH PRIVATE KEY----- ..."></textarea>
            </label>
            <label>
              <span>密钥口令</span>
              <input v-model.trim="form.key_passphrase" type="password" :disabled="!isKeyValue(form.auth_memthod)" placeholder="若私钥有口令则填写" />
            </label>
            <label>
              <span>系统</span>
              <select v-model="form.server_os">
                <option value="">请选择</option>
                <option v-for="d in dictOS" :key="d.dmm" :value="d.dmm">{{ d.dmmc }}</option>
              </select>
            </label>
            <label>
              <span>状态</span>
              <select v-model="form.status">
                <option value="">请选择</option>
                <option v-for="d in dictStatus" :key="d.dmm" :value="d.dmm">{{ d.dmmc }}</option>
              </select>
            </label>
          </div>
          <p class="muted" style="margin-top:6px;">提示：私钥仅用于控制台临时连接，当前不会保存到数据库。</p>
          <p class="msg" v-if="message">{{ message }}</p>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="closeModal">取消</button>
          <button class="btn primary" @click="onSubmit">保存</button>
        </div>
      </div>
    </div>

    <!-- 删除确认 -->
    <div v-if="confirmVisible" class="modal-backdrop" @click.stop>
      <div class="modal confirm-modal" @click.stop>
        <div class="modal-header warn"><h2>确认删除</h2></div>
        <div class="modal-body">
          <div class="confirm-content">
            <p class="confirm-text">确定要删除 “{{ confirmText }}” 吗？</p>
          </div>
          <p class="msg" v-if="message">{{ message }}</p>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="cancelConfirm">取消</button>
          <button class="btn warn" @click="doDelete">删除</button>
        </div>
      </div>
    </div>

    <!-- 控制台占位：WebSSH / WebRDP 色彩区分（使用 Teleport 到 body，确保最高层级显示） -->
    <teleport to="body">
      <div v-if="consoleVisible" class="modal-backdrop console-fullscreen" @click.stop>
        <div class="modal console-modal" :class="consoleType" @click.stop>
          <div class="modal-header" :class="consoleType">
            <h2>{{ consoleTitle }}</h2>
          </div>
          <div class="modal-body console-body" :class="consoleType">
            <div v-if="consoleType==='webssh'" class="terminal">
              <template v-if="!consoleCredOk">
                <div class="cred-form">
                  <div class="row">
                    <label>认证</label>
                    <select v-model="consoleAuth">
                      <option v-if="!dictAuth.length" value="password">口令</option>
                      <option v-if="!dictAuth.length" value="key">密钥</option>
                      <option v-for="d in dictAuth" :key="d.dmm" :value="d.dmm">{{ d.dmmc }}</option>
                    </select>
                  </div>
                  <div class="row">
                    <label>用户名</label>
                    <input v-model.trim="consoleUser" placeholder="root" />
                  </div>
                  <div class="row" v-if="consoleAuthIsPassword">
                    <label>密码</label>
                    <input v-model.trim="consolePass" type="password" placeholder="••••••" />
                  </div>
                  <div class="row" v-else>
                    <label>私钥</label>
                    <textarea v-model="consoleKey" class="ta" placeholder="粘贴私钥 (不会保存)"></textarea>
                  </div>
                  <div class="row" v-if="consoleAuthIsKey">
                    <label>口令</label>
                    <input v-model.trim="consoleKeyPass" type="password" placeholder="私钥口令(可选)" />
                  </div>
                  <div class="row">
                    <button class="btn primary" @click="startWebSSH">连接</button>
                  </div>
                  <p class="muted">目标：{{ consoleHost }}</p>
                </div>
              </template>
              <template v-else>
                <WebSSH :host="consoleIp" :port="consolePort" :user="consoleUser" :pass="consoleAuthIsPassword?consolePass:''" :auth="authForWs" :privateKey="consoleAuthIsKey?consoleKey:''" :keyPass="consoleAuthIsKey?consoleKeyPass:''" />
              </template>
            </div>
            <div v-else class="rdp">
              <p>WebRDP 占位：计划集成 Guacamole（后续提供）。</p>
              <p>目标主机：{{ consoleHost }}</p>
            </div>
          </div>
        </div>
      </div>
    </teleport>

  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, reactive, ref, computed, watch } from 'vue'
import api from '../../api'
import WebSSH from '../console/WebSSH.vue'

const list = ref([])
const q = reactive({ keyword: '', status: '', os: '' })
const dictOS = ref([])
const dictStatus = ref([])
const dictAuth = ref([])

const showModal = ref(false)
const editing = ref(false)
const editingId = ref(null)
const form = reactive({
  server_desc: '',
  server_ip: '',
  server_port: '',
  auth_memthod: 'password',
  server_user: '',
  server_pass: '',
  private_key: '', // 仅前端临时使用，不提交给后端保存
  key_passphrase: '', // 仅前端临时使用
  server_os: '',
  status: '1',
})
const message = ref('')

const confirmVisible = ref(false)
const confirmText = ref('')
const confirmItem = ref(null)

const consoleVisible = ref(false)
const consoleType = ref('webssh') // webssh | webrdp
const consoleTitle = ref('')
const consoleHost = ref('')
const consoleIp = ref('')
const consolePort = ref(22)
const consoleUser = ref('')
const consolePass = ref('')
const consoleCredOk = ref(false)
const consoleAuth = ref('password') // password | key
const consoleKey = ref('')
const consoleKeyPass = ref('')

// 新窗口：控制台窗口句柄
let consoleWin = null

function ensureConsoleWindow(urlOverride) {
  // 若已有并未被关闭，直接复用
  if (consoleWin && !consoleWin.closed) {
    try { consoleWin.focus() } catch {}
    return consoleWin
  }
  // 打开新窗口，指向当前应用但视图为 console
  const url = urlOverride || `${window.location.origin}${window.location.pathname}?view=console`
  consoleWin = window.open(url, 'ConsoleWindow', 'noopener,noreferrer')
  try { consoleWin && consoleWin.focus() } catch {}
  return consoleWin
}

function addTabToConsole(host) {
  // 若窗口未打开，带参数打开并让 ConsoleManager 自动创建首个会话
  let win
  if (!consoleWin || consoleWin.closed) {
    // 将主机信息通过查询参数传递（私钥使用 base64 以避免特殊字符）
    const sp = new URLSearchParams()
    sp.set('view','console')
    try {
      if (host?.server_ip) sp.set('h', host.server_ip)
      if (host?.server_port) sp.set('p', String(host.server_port||'22'))
      if (host?.server_user) sp.set('u', host.server_user)
      const auth = host?.auth_memthod || host?.auth_method || 'password'
      sp.set('a', String(auth))
      if (auth === 'key' || String(auth).toLowerCase().includes('key')) {
        const pk = host?.private_key || ''
        if (pk) sp.set('kb64', btoa(pk))
        if (host?.key_passphrase) sp.set('kpw', host.key_passphrase)
      } else {
        if (host?.server_pass) sp.set('pw', host.server_pass)
      }
    } catch {}
    const url = `${window.location.origin}${window.location.pathname}?${sp.toString()}`
    win = ensureConsoleWindow(url)
    return
  }
  // 已有窗口，调用其 addTab API
  win = ensureConsoleWindow()
  if (!win) return
  // 轮询等待子窗口暴露 addTab
  let tries = 0
  const timer = setInterval(() => {
    tries++
    try {
      if (win.closed) { clearInterval(timer); return }
      if (typeof win.addTab === 'function') {
        win.addTab(host)
        clearInterval(timer)
        return
      }
    } catch {}
    if (tries > 50) { // 最长约10秒
      clearInterval(timer)
    }
  }, 200)
}

// 认证方式（字典06）联动辅助：识别密钥/口令类型
function isKeyValue(val) {
  if (!val) return false
  if (val === 'key') return true
  const d = (dictAuth.value || []).find(x => x.dmm === val)
  const name = String(d?.dmmc || '').toLowerCase()
  return name.includes('密钥') || name.includes('key')
}
function isPasswordValue(val) {
  if (!val) return true
  if (val === 'password') return true
  const d = (dictAuth.value || []).find(x => x.dmm === val)
  const name = String(d?.dmmc || '').toLowerCase()
  return !(name.includes('密钥') || name.includes('key'))
}
const consoleAuthIsKey = computed(() => isKeyValue(consoleAuth.value))
const consoleAuthIsPassword = computed(() => isPasswordValue(consoleAuth.value))
const authForWs = computed(() => (consoleAuthIsKey.value ? 'key' : 'password'))

const filtered = computed(() => {
  const kw = (q.keyword || '').toLowerCase()
  return (list.value || []).filter(it => {
    const okKw = !kw || `${it.server_desc||''} ${it.server_ip||''} ${it.server_port||''}`.toLowerCase().includes(kw)
    const okSt = !q.status || it.status === q.status
    const okOs = !q.os || it.server_os === q.os
    return okKw && okSt && okOs
  })
})

// 分页
const page = ref(1)
const pageSize = ref(10)
const totalPages = computed(() => Math.max(1, Math.ceil((filtered.value.length || 0) / (Number(pageSize.value) || 1))))
const paged = computed(() => {
  const p = Math.min(Math.max(1, Number(page.value) || 1), Number(totalPages.value) || 1)
  const ps = Number(pageSize.value) || 20
  const start = (p - 1) * ps
  return (filtered.value || []).slice(start, start + ps)
})

watch([filtered, pageSize], () => {
  // 当过滤结果或每页数量变化时重置/修正页码
  page.value = 1
})

function onPrev() { if (page.value > 1) page.value-- }
function onNext() { if (page.value < totalPages.value) page.value++ }
function onPageSizeChange(e) {
  const v = Number(e?.target?.value) || 20
  pageSize.value = v
  page.value = 1
}
function onJump(e) {
  try {
    const val = Number((e && e.target && e.target.value) || 0)
    if (!val) return
    const tp = Number(totalPages.value) || 1
    const target = Math.max(1, Math.min(tp, val))
    page.value = target
  } catch {}
}

function labelOf(arrRef, value) {
  const arr = Array.isArray(arrRef) ? arrRef : arrRef?.value
  const f = (arr || []).find(i => i.dmm === (value ?? ''))
  return f?.dmmc || value || ''
}

async function fetchDicts() {
  try {
    const [osRes, stRes, auRes] = await Promise.all([
      api.get('/dicts/04'),
      api.get('/dicts/05'),
      api.get('/dicts/06'),
    ])
    // 直接使用 SQL 查询结果：dmm 为值，dmmc 为显示
    dictOS.value = Array.isArray(osRes.data) ? osRes.data : []
    dictStatus.value = Array.isArray(stRes.data) ? stRes.data : []
    dictAuth.value = Array.isArray(auRes.data) ? auRes.data : []
  } catch (e) {
    message.value = '加载字典失败: ' + (e?.response?.data?.detail || e.message)
  }
}

async function fetchList() {
  try {
    const { data } = await api.get('/servers/')
    list.value = data
  } catch (e) {
    message.value = '加载失败: ' + (e?.response?.data?.detail || e.message)
  }
}

function onQuery() { fetchList() }
function onCreate() {
  editing.value = false
  editingId.value = null
  form.server_desc = ''
  form.server_ip = ''
  form.server_port = ''
  form.auth_memthod = 'password'
  form.server_user = ''
  form.server_pass = ''
  form.private_key = ''
  form.key_passphrase = ''
  form.server_os = ''
  form.status = '1'
  message.value = ''
  showModal.value = true
}
function closeModal() { showModal.value = false }

async function onSubmit() {
  try {
    if (!form.server_ip) return (message.value = '请填写地址')
    if (!form.server_port) return (message.value = '请填写端口')
    if (!form.server_user) return (message.value = '请填写用户名')
    if (isPasswordValue(form.auth_memthod)) {
      if (!form.server_pass && !editing.value) return (message.value = '请填写口令')
    } else if (isKeyValue(form.auth_memthod)) {
      if (!form.private_key) return (message.value = '请粘贴私钥')
    }
    if (!form.server_os) return (message.value = '请选择系统')
    if (!form.status) return (message.value = '请选择状态')

    if (editing.value && editingId.value) {
      const payload = { ...form }
      // 私钥信息不保存，仅用于控制台临时连接
      delete payload.private_key
      delete payload.key_passphrase
      if (form.auth_memthod === 'key') {
        // 密钥认证时不更新保存口令
        delete payload.server_pass
      }
      if (!payload.server_pass || String(payload.server_pass).trim() === '') {
        delete payload.server_pass
      }
      await api.put(`/servers/${editingId.value}`, payload)
    } else {
      const payload = { ...form }
      delete payload.private_key
      delete payload.key_passphrase
      if (form.auth_memthod === 'key') {
        delete payload.server_pass
      }
      await api.post('/servers/', payload)
    }
    await fetchList()
    closeModal()
  } catch (e) {
    message.value = '提交失败: ' + (e?.response?.data?.detail || e.message)
  }
}

function onEdit(item) {
  editing.value = true
  editingId.value = item.id
  form.server_desc = item.server_desc || ''
  form.server_ip = item.server_ip || ''
  form.server_port = item.server_port || ''
  form.auth_memthod = item.auth_memthod || 'password'
  form.server_user = item.server_user || ''
  form.server_pass = ''
  form.private_key = ''
  form.key_passphrase = ''
  form.server_os = item.server_os || ''
  form.status = item.status || ''
  message.value = ''
  showModal.value = true
}

function onDelete(item) {
  confirmItem.value = item
  confirmText.value = item.server_desc || `${item.server_ip}:${item.server_port}`
  confirmVisible.value = true
}
function cancelConfirm() { confirmVisible.value = false; confirmItem.value = null; confirmText.value = '' }
async function doDelete() {
  try {
    await api.delete(`/servers/${confirmItem.value.id}`)
    cancelConfirm()
    await fetchList()
  } catch (e) {
    message.value = '删除失败: ' + (e?.response?.data?.detail || e.message)
  }
}

async function onTest(item) {
  try {
    const { data } = await api.post(`/servers/${item.id}/test`)
    message.value = data?.success ? '连接成功' : '连接失败'
  } catch (e) {
    message.value = '测试失败: ' + (e?.response?.data?.detail || e.message)
  }
}

function onConsole(item) {
  // 改为在独立窗口中的多标签控制台打开该主机
  addTabToConsole(item)
}

function startWebSSH() {
  if (!consoleUser.value) return (message.value = '请输入用户名')
  if (consoleAuth.value === 'key' || consoleAuthIsKey.value) {
    if (!consoleKey.value) return (message.value = '请粘贴私钥')
  } else if (consoleAuthIsPassword.value) {
    if (!consolePass.value) return (message.value = '请输入密码')
  }
  consoleCredOk.value = true
  // 触发 xterm 适配
  setTimeout(() => window.dispatchEvent(new Event('resize')), 0)
}

function closeConsole() { 
  consoleVisible.value = false 
  // 恢复页面滚动
  document.body.style.overflow = ''
}

onMounted(async () => {
  await fetchList()
  await fetchDicts()

  // 监听 WebSSH exit 事件，自动关闭控制台（命名函数便于移除监听）
  const onWebsshExit = () => {
    if (consoleVisible.value) {
      closeConsole()
    }
  }
  window.addEventListener('webssh-exit', onWebsshExit)

  // 在组件卸载时移除事件监听，避免内存泄漏
  onBeforeUnmount(() => {
    try { window.removeEventListener('webssh-exit', onWebsshExit) } catch {}
  })
})
</script>

<style scoped>
.host-mgr { display: flex; flex-direction: column; gap: 12px; }
.card { background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; padding: 12px; }
.toolbar .row { display: flex; gap: 8px; align-items: center; }
.table-wrap { overflow: auto; max-height: 60vh; }
/* 控制台弹窗样式 */
.console-modal { width: 90vw; max-width: 1200px; }
.console-body { padding: 0 12px 12px; }
.cred-form { display: flex; flex-direction: column; gap: 10px; }
.cred-form .row { display: flex; gap: 8px; align-items: center; }
.cred-form label { width: 64px; color: #555; }
.cred-form input { flex: 1; height: 30px; border: 1px solid #e5e7eb; border-radius: 6px; padding: 0 8px; }
.field { position: relative; display: inline-flex; align-items: center; }
.field .leading { position: absolute; left: 8px; color: #64748b; }
.ipt { height: 30px; padding: 0 10px; border: 1px solid #c7d2fe; border-radius: 6px; width: 280px; }
.ipt.with-icon { padding-left: 30px; }
.sel { height: 30px; padding: 0 8px; border: 1px solid #c7d2fe; border-radius: 6px; }
.sel.with-icon { padding-left: 30px; }
.btn { height: 30px; padding: 0 12px; border: 1px solid #d0d7de; border-radius: 6px; background: #fff; cursor: pointer; }
.btn.icon { display: inline-flex; align-items: center; gap: 6px; }
.btn:hover { background: #f8fafc; }
.btn.primary { background: #e8f0fe; border-color: #3b82f6; color: #0b57d0; }
.icon-btn { display: inline-flex; align-items: center; justify-content: center; width: 30px; height: 30px; padding: 0; border-radius: 6px; border: 1px solid #e5e7eb; background: #ffffff; color: #475569; cursor: pointer; }
.icon-btn:hover { background: #f8fafc; border-color: #cbd5e1; color: #0f172a; }
.icon-btn.primary { color: #0b57d0; border-color: #93c5fd; background: #eff6ff; }
.icon-btn.primary:hover { color: #0a46ab; border-color: #60a5fa; background: #dbeafe; }
.table { width: 100%; min-width: 980px; border-collapse: separate; border-spacing: 0; table-layout: fixed; font-size: 14px; }
.table thead th { background: #f5f7ff; color: #0b57d0; font-weight: 500; border-bottom: 1px solid #e5e7eb; }
.table th, .table td { padding: 8px 10px; border-bottom: 1px solid #eee; text-align: left; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.empty { text-align: center; color: #888; }
.op-col { width: 160px; }
.op-col .icon-btn { display: inline-flex; align-items: center; justify-content: center; width: 26px; height: 26px; padding: 0; border-radius: 6px; border: 1px solid #e5e7eb; background: #ffffff; color: #475569; cursor: pointer; }
.op-col .icon-btn:hover { background: #f8fafc; border-color: #cbd5e1; color: #0f172a; }
.op-col .icon-btn.info { color: #0b57d0; border-color: #93c5fd; background: #eff6ff; }
.op-col .icon-btn.info:hover { color: #0a46ab; border-color: #60a5fa; background: #dbeafe; }
.op-col .icon-btn.warn { color: #dc2626; border-color: #fecaca; background: #fff1f2; }
.op-col .icon-btn.warn:hover { color: #b91c1c; border-color: #fca5a5; background: #ffe4e6; }
.op-col .icon-btn.success { color: #16a34a; border-color: #bbf7d0; background: #f0fdf4; }
.op-col .icon-btn.success:hover { color: #15803d; border-color: #86efac; background: #dcfce7; }
.op-col .icon-btn.console { color: #7c3aed; border-color: #c4b5fd; background: #f5f3ff; }
.op-col .icon-btn.console:hover { color: #6d28d9; border-color: #a78bfa; background: #ede9fe; }

.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.35); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal { width: 720px; max-width: 92vw; background: #fff; border-radius: 12px; overflow: hidden; }
.console-modal { width: 100vw; height: 100vh; max-width: 100vw; max-height: 100vh; border-radius: 0; }
.modal-backdrop.console-fullscreen { 
  align-items: stretch; 
  justify-content: stretch; 
  background: transparent; 
  z-index: 2147483647; 
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
}
.modal-header { padding: 12px 16px; border-bottom: 1px solid #e0e7ff; background: #f5f7ff; }
.modal-header h2 { margin: 0; font-size: 16px; line-height: 20px; font-weight: 600; color: #0b57d0; }
.modal-body { padding: 16px; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 10px; }
.grid label { display: flex; flex-direction: column; gap: 6px; }
.grid input, .grid select { height: 30px; padding: 0 10px; border: 1px solid #c7d2fe; border-radius: 6px; }
.modal-actions { padding: 0 16px 16px; display: flex; justify-content: center; gap: 10px; }
.msg { margin-top: 8px; color: #b91c1c; }

/* 控制台配色：webssh 深色、webrdp 蓝色 */
.console-modal { display: flex; flex-direction: column; }
.console-modal .modal-body { flex: 1; padding: 0; overflow: hidden; }
.console-modal.webssh .modal-header { background: #0b1220; border-bottom-color: #1e293b; }
.console-modal.webssh .modal-header h2 { color: #34d399; }
.console-modal.webssh .console-body { background: #0b1220; color: #e5e7eb; height: 100%; }
.console-modal.webssh .terminal { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; color: #a7f3d0; height: 100%; }

.console-modal.webrdp .modal-header { background: #e6f0ff; border-bottom-color: #c7d2fe; }
.console-modal.webrdp .modal-header h2 { color: #0b57d0; }
.console-modal.webrdp .console-body { background: #f4f8ff; color: #0f172a; }

/* 分页样式（与连接管理 ConnTable.vue 完全一致） */
.tq-pagination { display: flex; align-items: center; gap: 8px; width: 100%; margin-top: 10px; padding-top: 8px; text-align: left; flex: 0 0 auto; position: static; background: transparent; border-top: 1px solid #e5e7eb; }
.tq-pagination .muted { color: #64748b; }
.tq-pagination select { color: #0b57d0; font-weight: 400; font-size: 14px; height: 28px; }
</style>
