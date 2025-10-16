<template>
  <div class="webssh" ref="wrap">
    <div ref="termEl" class="term"></div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'

const props = defineProps({
  host: { type: String, required: true },
  port: { type: [String, Number], default: 22 },
  user: { type: String, required: true },
  pass: { type: String, default: '' },
  auth: { type: String, default: 'password' }, // password | key
  privateKey: { type: String, default: '' }, // private key content
  keyPass: { type: String, default: '' }, // key passphrase
  tabId: { type: String, default: '' }, // optional: identify parent tab
  showConnectBanner: { type: Boolean, default: true }, // 模拟 Xshell 的连接提示
  customBanner: { type: String, default: '' }, // 自定义横幅文本（可多行），若设置则优先生效
  autoLastLogin: { type: Boolean, default: true }, // 自动生成 Last login 行
  autoWelcomeText: { type: String, default: '' }, // 自动欢迎语（如: Welcome to Alibaba Cloud ...）
  setPromptWithPath: { type: Boolean, default: false }, // 可选：连接后设置远端 PS1 展示当前目录
})

const termEl = ref(null)
const wrap = ref(null)
let term, fitAddon, ws
let keepTimer = null
let hasExited = false
let connectedAt = 0
let reactivatedAt = 0
let reactBuf = ''
let reactBufTimer = null
let lastInputAt = 0
let lastOutChunkAt = 0
let lastOutTail = ''
let firstOutputAt = 0
// 提示符分段组装（独立于激活窗口）：识别诸如 "\t[hopson@bac" 的未闭合片段
let pendingPromptBuf = ''
let pendingPromptTimer = null
let pendingPromptAt = 0
let connecting = false // 避免在重连或挂载过程中重复建立连接

// 颜色：用户名绿色、主机蓝色、路径青色
const ANSI = {
  reset: '\u001b[0m',
  green: '\u001b[32m',
  blue: '\u001b[34m',
  cyan: '\u001b[36m',
}

function stripANSICodes(s){
  try {
    return s
      .replace(/\u001b\[[0-9;?]*[ -\/]*[@-~]/g, '') // CSI
      .replace(/\u001b\][^\u0007\u001b]*(?:\u0007|\u001b\\)/g, '') // OSC
      .replace(/[\x00-\x08\x0B-\x0C\x0E-\x1F]/g, '') // other controls
  } catch { return s }
}

// 将形如 "[user@host path]$" 或 "]#" 的提示符本地着色
function colorizePromptIfAny(text){
  try {
    const plain = stripANSICodes(text)
    const parts = plain.split(/\r?\n/)
    if (!parts.length) return text
    const last = parts[parts.length-1]
    // 匹配 [user@host path]$ 或 # 结尾
    // 允许可选的环境名前缀，如 "(base) "，再跟标准的 [user@host path] 提示符
    const m = last.match(/^\s*(?:\([^()\r\n]{1,32}\)\s*)?\([^@\]\r\n]{1,64}\)@([^\]\s\r\n]{1,128})\s+([^\]\r\n]{1,256})\]\s*([#$%]\s*)?$/)
    if (!m) return text
    const [, user, host, path, tail = ''] = m
    const colored = `${ANSI.green}${user}${ANSI.reset}`
      + '@'
      + `${ANSI.blue}${host}${ANSI.reset}`
      + ' '
      + `${ANSI.cyan}${path}${ANSI.reset}`
    const rebuilt = last.replace(/\[[^\]]*\]/, `[${colored}]`)
    parts[parts.length-1] = rebuilt
    return parts.join('\r\n')
  } catch {
    return text
  }
}

function buildWsUrl() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
  const base = `${proto}//${location.host}`
  const q = new URLSearchParams({
    host: String(props.host || ''),
    port: String(props.port || '22'),
    user: String(props.user || ''),
    pass: String(props.pass || ''),
    auth: String(props.auth || 'password'),
  })
  if ((props.auth || 'password') === 'key') {
    try {
      const key_b64 = btoa(props.privateKey || '')
      if (key_b64) q.set('key_b64', key_b64)
      if (props.keyPass) q.set('key_pass', props.keyPass)
    } catch (e) {
      // ignore encode error
    }
  }
  return `${base}/api/ssh/ws?${q.toString()}`
}

function connect() {
  if (connecting) return
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return
  connecting = true
  // 若存在旧连接，先彻底关闭并清理
  try {
    if (ws) {
      try { ws.onopen = ws.onmessage = ws.onerror = ws.onclose = null } catch {}
      try { ws.close() } catch {}
    }
    ws = null
    if (keepTimer) { clearInterval(keepTimer); keepTimer = null }
  } catch {}
  const url = buildWsUrl()
  // 在建立连接前输出类似 Xshell 的提示（仅终端本地显示，不向服务器发送任何数据）
  try {
    if (props.showConnectBanner) {
      const host = String(props.host || '')
      const port = String(props.port || '22')
      term?.write(`Connecting to ${host}:${port}...\r\n`)
    }
  } catch {}
  ws = new WebSocket(url)
  ws.onopen = () => {
    connecting = false
    hasExited = false
    connectedAt = Date.now()
    doFit()
    // 心跳，避免某些代理/网关在空闲时立即断开
    try {
      if (keepTimer) { clearInterval(keepTimer) }
      keepTimer = setInterval(() => {
        try { if (ws && ws.readyState === WebSocket.OPEN) ws.send('__PING__') } catch {}
      }, 30000)
    } catch {}
    // 本地输出连接已建立与快捷键提示（不向远端发送回车）
    try {
      if (props.showConnectBanner) {
        term?.write('Connection established.\r\n')
        term?.write("To escape to local shell, press 'Ctrl+Alt+]'.\r\n\r\n")
        const lines = []
        if (props.customBanner && props.customBanner.trim()) {
          lines.push(props.customBanner.trim())
        } else {
          if (props.autoLastLogin) {
            const d = new Date()
            const pad = (n)=> String(n).padStart(2,'0')
            const dow = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][d.getDay()]
            const mon = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getMonth()]
            const fmt = `${dow} ${mon} ${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())} ${d.getFullYear()}`
            const from = (location && location.hostname) ? location.hostname : 'webssh'
            lines.push(`Last login: ${fmt} from ${from}`)
          }
          if (props.autoWelcomeText && props.autoWelcomeText.trim()) {
            lines.push(props.autoWelcomeText.trim())
          }
        }
        if (lines.length) {
          const text = lines.join('\r\n') + '\r\n\r\n'
          term?.write(text)
        }
      }
    } catch {}
    // 可选：设置 PS1（默认关闭）
    try {
      if (props.setPromptWithPath && ws && ws.readyState === WebSocket.OPEN) {
        const cmd = "export PS1='[\\u@\\h \\w]\\$ '" + '\r'
        ws.send(cmd)
      }
    } catch {}
  }
  ws.onmessage = (ev) => {
    if (typeof ev.data === 'string') {
      // 先做“提示符分段组装”：无论是否处于 re-activate 窗口
      try {
        // 移除常见控制序列：CSI、OSC(到 BEL 或 ST)、以及常见控制字符
        const stripANSI = (s) => s
          // CSI: ESC [ ... cmd
          .replace(/\u001b\[[0-9;?]*[ -/]*[@-~]/g, '')
          // OSC: ESC ] ... BEL
          .replace(/\u001b\][^\u0007\u001b]*(?:\u0007|\u001b\\)/g, '')
          // 其他低位控制符（保留\t以支持缩进识别）
          .replace(/[\x00-\x08\x0B-\x0C\x0E-\x1F]/g, '')
        const hasNL = (s) => /\r|\n/.test(s)
        // 基于“最后一行”判断提示符是否未闭合
        const looksPromptStart = (s) => {
          const t = s.replace(/\s+$/,'')
          const parts = t.split(/\r?\n/)
          const last = (parts[parts.length-1] || '').replace(/^\s+/, '')
          // 形如 "[user@hos"（无右括号）视为未闭合提示符
          return /^\[[^\]\r\n]{0,120}@[^^\]\r\n]{0,120}$/.test(last)
        }
        const looksPromptComplete = (s) => {
          const parts = s.split(/\r?\n/)
          const last = (parts[parts.length-1] || '').replace(/^\s+/, '')
          return /\]/.test(last) || /[#$%] $/.test(last)
        }

        const incoming = ev.data
        if (pendingPromptBuf) {
          const combined = pendingPromptBuf + incoming
          const combinedStripped = stripANSI(combined)
          if (looksPromptComplete(combinedStripped)) {
            // 完整了再一次性输出（本地着色提示符）
            const out = colorizePromptIfAny(combined)
            term?.write(out)
            if (pendingPromptTimer) { clearTimeout(pendingPromptTimer); pendingPromptTimer = null }
            pendingPromptBuf = ''
            pendingPromptAt = 0
            return
          } else {
            // 继续缓冲，重置超时；到期仍不完整则放弃，避免显示半截
            pendingPromptBuf = combined
            if (pendingPromptTimer) { clearTimeout(pendingPromptTimer) }
            pendingPromptTimer = setTimeout(() => {
              try { pendingPromptBuf = '' } finally { if (pendingPromptTimer) { clearTimeout(pendingPromptTimer); pendingPromptTimer = null } pendingPromptAt = 0 }
            }, 6000)
            return
          }
        } else {
          const stripped = stripANSI(incoming)
          // 情况A：整个 chunk 的“最后一行”是未闭合提示符（原有规则）
          const caseA = looksPromptStart(stripped)
          // 情况B：chunk 中间某一行正好以未闭合提示符结尾，且其后续内容不含 ']'（跨行分裂的主机名），为了避免闪烁，整块缓冲
          let caseB = false
          try {
            const parts = stripped.split(/\r?\n/)
            for (let i=0;i<parts.length;i++){
              const line = (parts[i]||'').replace(/^\s+/, '')
              if (/^\[[^\]\r\n]{0,120}@[^^\]\r\n]{0,120}$/.test(line)){
                const rest = parts.slice(i+1).join('\n')
                if (!/\]/.test(rest)) { caseB = true; break }
              }
            }
          } catch {}
          if (caseA || caseB) {
            pendingPromptBuf = incoming
            pendingPromptAt = Date.now()
            if (pendingPromptTimer) { clearTimeout(pendingPromptTimer) }
            pendingPromptTimer = setTimeout(() => {
              try { pendingPromptBuf = '' } finally { if (pendingPromptTimer) { clearTimeout(pendingPromptTimer); pendingPromptTimer = null } pendingPromptAt = 0 }
            }, 6000)
            return
          }
        }
      } catch {}
      // 识别后端的退出消息 {type:'exit', code}
      try {
        const msg = JSON.parse(ev.data)
        if (msg && msg.type === 'exit') {
          hasExited = true
          // 通知外层：会话已退出
          try { window.dispatchEvent(new CustomEvent('webssh-exit', { detail: { tabId: props.tabId || '' } })) } catch {}
          return
        }
      } catch (_) {
        // 非 JSON，当作普通输出
      }
      // 某些环境下会在连接或标签切换后短时间内回显无意义的 "bac"，做一次更稳健的过滤
      try {
        const now = Date.now()
        const dt = now - (connectedAt || 0)
        const dr = now - (reactivatedAt || 0)
        // 去除常见 ANSI 控制序列和换行以便判断
        const cleaned = ev.data.replace(/\u001b\[[0-9;]*[A-Za-z]/g, '')
        const cleanedFlat = cleaned.replace(/\r|\n/g, '').trim()
        // 近 3 秒内是否有用户输入
        const sinceInput = now - (lastInputAt || 0)
        const noRecentInput = isFinite(sinceInput) ? sinceInput > 3000 : true
        // 近 1200ms 是否刚输出过以 @ 结尾（提示符用户名@主机名的前半段）
        const sinceOut = now - (lastOutChunkAt || 0)
        const looksLikePromptHead = /@?$/.test(lastOutTail) && lastOutTail.includes('@')

        // 条件：
        // 1) 在刚连接/刚激活的短窗口内，或
        // 2) 无用户输入的静默期，且不太像提示符延续，
        // 则丢弃孤立的 'bac' 片段（仅针对完全等于 'bac' 的片段，避免误伤）
        const inEarlyWindow = (dt <= 15000 || dr <= 8000)
        const promptContinuationLikely = looksLikePromptHead && sinceOut <= 1200
        if (cleanedFlat === 'bac') {
          if (inEarlyWindow) return
          if (noRecentInput && !promptContinuationLikely) return
        }
      } catch {}
      // 在刚被重新激活后的短时间内，对输出做行级缓冲，避免显示半截提示符（如 [hopson@bac）
      try {
        const now2 = Date.now()
        const dr2 = now2 - (reactivatedAt || 0)
        const windowMs = 4000
        const withinWindow = dr2 >= 0 && dr2 <= windowMs
        if (withinWindow) {
          // 先缓冲
          reactBuf += ev.data
          // 如果包含换行，先检查是否仍是未闭合提示符片段；若是，则继续缓冲，避免将一行拆成两行
          if (/\r|\n/.test(reactBuf)) {
            const strippedNL = reactBuf.replace(/\u001b\[[0-9;]*[A-Za-z]/g, '')
            const lines = strippedNL.split(/\r?\n/)
            const lastLine = lines[lines.length - 1] || ''
            const lastTrimHead = lastLine.replace(/^\s+/, '')
            const bracketIncompleteNL = /^\[[^\]\r\n]{0,120}$/.test(lastTrimHead) && lastTrimHead.includes('@') && !lastTrimHead.includes(']')
            const endsWithPromptNL = /[#$%] $/.test(lastTrimHead)
            if (!bracketIncompleteNL || endsWithPromptNL) {
              // 输出缓冲（本地着色提示符）
              const out = colorizePromptIfAny(reactBuf)
              term?.write(out)
              reactBuf = ''
              if (reactBufTimer) { clearTimeout(reactBufTimer); reactBufTimer = null }
              return
            }
            // 若未闭合，继续等后续片段合并后再输出
          }
          // 启动/重置一个短超时；在窗口内尽量等到“完整提示符”再输出
          if (reactBufTimer) { clearTimeout(reactBufTimer); reactBufTimer = null }
          reactBufTimer = setTimeout(() => {
            try {
              const stripped = reactBuf.replace(/\u001b\[[0-9;]*[A-Za-z]/g, '')
              const hasNewline = /\r|\n/.test(stripped)
              const strippedHeadTrim = stripped.replace(/^\s+/, '')
              const endsWithPrompt = /[#$%] $/.test(strippedHeadTrim)
              const bracketComplete = /^\[[^\]\r\n]{1,120}\][^\r\n]*$/.test(strippedHeadTrim) // 包含 ] 视为完整
              const bracketIncomplete = /^\[[^\]\r\n]{0,120}$/.test(strippedHeadTrim) && strippedHeadTrim.includes('@') && !strippedHeadTrim.includes(']')

              const now3 = Date.now()
              const dr3 = now3 - (reactivatedAt || 0)
              const stillInWindow = dr3 >= 0 && dr3 <= windowMs

              if (hasNewline || bracketComplete || endsWithPrompt) {
                // 判定为完整，输出
                // 若缓冲内容实际上只是杂散的 'bac' 短片段（无换行），则丢弃
                const flatShort = stripped.replace(/\r|\n/g, '').trim()
                if (flatShort === 'bac' && !hasNewline) {
                  reactBuf = ''
                } else {
                  const out = colorizePromptIfAny(reactBuf)
                  term?.write(out)
                  reactBuf = ''
                }
              } else if (stillInWindow) {
                // 仍在窗口内但不完整：继续等待下一批数据
                if (reactBufTimer) { clearTimeout(reactBufTimer) }
                reactBufTimer = setTimeout(() => {
                  try {
                    const s2 = reactBuf.replace(/\u001b\[[0-9;]*[A-Za-z]/g, '')
                    const hasNL2 = /\r|\n/.test(s2)
                    const s2HeadTrim = s2.replace(/^\s+/, '')
                    const endsPrompt2 = /[#$%] $/.test(s2HeadTrim)
                    const bracketComplete2 = /^\[[^\]\r\n]{1,120}\][^\r\n]*$/.test(s2HeadTrim)
                    const now4 = Date.now()
                    const dr4 = now4 - (reactivatedAt || 0)
                    const stillWin2 = dr4 >= 0 && dr4 <= windowMs
                    if (hasNL2 || bracketComplete2 || endsPrompt2 || !stillWin2) {
                      // 最终输出（或窗口结束时做最终决定）
                      const flat2 = s2.replace(/\r|\n/g, '').trim()
                      if (flat2 === 'bac' && !hasNL2) {
                        reactBuf = ''
                      } else {
                        const out = colorizePromptIfAny(reactBuf)
                        term?.write(out)
                        reactBuf = ''
                      }
                    }
                  } finally {
                    if (reactBufTimer) { clearTimeout(reactBufTimer) }
                    reactBufTimer = null
                  }
                }, 220)
              } else {
                // 窗口已结束：若是明显无意义的短片段或未闭合提示符，则丢弃；否则输出
                const noNewline = !hasNewline
                const flat3 = stripped.replace(/\r|\n/g, '').trim()
                if (flat3 === 'bac') {
                  reactBuf = ''
                } else if ((noNewline && stripped.length <= 24) || bracketIncomplete) {
                  reactBuf = ''
                } else if (reactBuf) {
                  term?.write(reactBuf)
                  reactBuf = ''
                }
              }
            } finally {
              if (reactBufTimer) { clearTimeout(reactBufTimer) }
              reactBufTimer = null
            }
          }, 200)
          return
        }
      } catch {}
      // 记录首次输出时间 & 输出尾部若干字符用于上下文判断
      try {
        if (!firstOutputAt) firstOutputAt = Date.now()
        const s = ev.data.replace(/\u001b\[[0-9;]*[A-Za-z]/g, '')
        const flat = s.replace(/\r|\n/g, '')
        lastOutTail = flat.slice(-4)
        lastOutChunkAt = Date.now()
      } catch {}
      // 普通输出路径：对完整提示符行做本地着色；其它内容保持原样
      try {
        const out = colorizePromptIfAny(ev.data)
        term?.write(out)
      } catch {
        term?.write(ev.data)
      }
    }
  }
  ws.onerror = () => {
    // 静默处理终端横幅，保留事件/日志
    try { console.error('[WebSSH] websocket error') } catch {}
  }
  ws.onclose = () => {
    connecting = false
    try { if (keepTimer) { clearInterval(keepTimer); keepTimer = null } } catch {}
    // 静默处理关闭横幅，仅派发退出事件（如未收到 exit）
    try { if (!hasExited) window.dispatchEvent(new CustomEvent('webssh-exit', { detail: { tabId: props.tabId || '' } })) } catch {}
  }
}

function isVisible(el){
  if (!el) return false
  const rect = el.getBoundingClientRect?.()
  if (!rect) return false
  const hasSize = rect.width > 0 && rect.height > 0
  const displayed = el.offsetParent !== null || (rect.width > 0 && rect.height > 0)
  return hasSize && displayed
}

function doFit() {
  if (!fitAddon || !term) return
  try {
    // 若容器不可见或尺寸为 0，跳过本次 fit，避免把终端尺寸缩到极小导致折行
    if (!isVisible(wrap.value)) return
    fitAddon.fit()
    const cols = term.cols
    const rows = term.rows
    // 保护：异常情况下列数过小（例如 < 20 列）也不向后端发送，避免远端重绘造成提示符断行
    if (cols >= 20 && rows >= 2 && ws && ws.readyState === WebSocket.OPEN) {
      ws.send(`__RESIZE__:${cols}x${rows}`)
    }
  } catch {}
}

onMounted(() => {
  term = new Terminal({
    convertEol: false,
    cursorBlink: true,
    cursorStyle: 'block',
    fontFamily: 'Menlo, Consolas, monospace',
    fontSize: (window.__dv_font_mono_px || 15),
    lineHeight: 1.0,
    windowsMode: true,
    theme: {
      background: '#0b1021',
      foreground: '#e6e6e6',
      cursor: '#ffffff',
      cursorAccent: '#0b1021',
      selection: '#ffffff40',
      black: '#000000',
      red: '#ff5555',
      green: '#50fa7b',
      yellow: '#f1fa8c',
      blue: '#bd93f9',
      magenta: '#ff79c6',
      cyan: '#8be9fd',
      white: '#bfbfbf',
      brightBlack: '#4d4d4d',
      brightRed: '#ff6e67',
      brightGreen: '#5af78e',
      brightYellow: '#f4f99d',
      brightBlue: '#caa9fa',
      brightMagenta: '#ff92d0',
      brightCyan: '#9aedfe',
      brightWhite: '#ffffff',
    },
  })
  fitAddon = new FitAddon()
  term.loadAddon(fitAddon)
  term.open(termEl.value)
  term.focus()

  // 同步 xterm 的 resize 事件到后端，避免尺寸不同步造成折行/回车重绘
  try {
    term.onResize(({ cols, rows }) => {
      try {
        if (ws && ws.readyState === WebSocket.OPEN && cols >= 20 && rows >= 2) {
          ws.send(`__RESIZE__:${cols}x${rows}`)
        }
      } catch {}
    })
  } catch {}

  // 在渲染初期与字体就绪后多次触发 fit + resize，提高初次同步成功率
  const burstFit = () => { try { doFit() } catch {} }
  // 立即 & 下一个动画帧 & 若干延迟重试
  burstFit()
  try { requestAnimationFrame(burstFit) } catch {}
  setTimeout(burstFit, 50)
  setTimeout(burstFit, 180)
  setTimeout(burstFit, 400)
  setTimeout(burstFit, 800)
  // 字体加载就绪后再 fit 一次
  try { document?.fonts?.ready?.then(() => setTimeout(burstFit, 0)) } catch {}

  // 监听全局字体缩放
  try {
    const onScale = (e) => {
      try {
        const mono = (e?.detail?.monoPx) || (window.__dv_font_mono_px) || 15
        term?.setOption('fontSize', mono)
        setTimeout(() => { try { doFit() } catch {} }, 0)
      } catch {}
    }
    window.addEventListener('dv-fontscale-change', onScale)
    wrap.value.__onFontScale = onScale
  } catch {}
  // 阻止浏览器快捷键透传
  try{
    term.attachCustomKeyEventHandler((e)=>{
      const k = e.key
      const ctrl = !!e.ctrlKey
      const shift = !!e.shiftKey
      const alt = !!e.altKey
      if (ctrl && alt && (k === ']' || e.code === 'BracketRight')){
        try { e.preventDefault?.() } catch {}
        try { ws && ws.close() } catch {}
        try { window.dispatchEvent(new CustomEvent('webssh-exit', { detail: { tabId: props.tabId || '' } })) } catch {}
        try { term?.write("\r\n[Disconnected by Ctrl+Alt+]]\r\n") } catch {}
        return false
      }
      if (k === 'F12') return false
      if (k === 'F5') return false
      if (ctrl && (k === 'r' || k === 'R')) return false
      if (ctrl && shift && (k === 'I' || k === 'J' || k === 'C')) return false
      if (ctrl && shift && (k === 'R' || k === 'F5')) return false
      if (alt && k === 'F4') return false
      return true
    })
  }catch{}
  let inputBuffer = ''
  term.onData(data => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(data)
      lastInputAt = Date.now()
      if (data.charCodeAt(0) === 13) {
        if (inputBuffer.trim() === 'exit') {
          setTimeout(() => {
            window.dispatchEvent(new CustomEvent('webssh-exit'))
          }, 1000)
        }
        inputBuffer = ''
      } else if (data.charCodeAt(0) === 127 || data.charCodeAt(0) === 8) {
        inputBuffer = inputBuffer.slice(0, -1)
      } else if (data.charCodeAt(0) >= 32) {
        inputBuffer += data
      }
    }
  })
  const ro = new ResizeObserver(() => {
    try {
      if (isVisible(wrap.value)) doFit()
    } catch {}
  })
  ro.observe(wrap.value)
  wrap.value.__ro = ro

  connect()
  setTimeout(() => { try { doFit(); term?.refresh(0, term.rows-1) } catch {} }, 50)

  const onTabActive = (e) => {
    try {
      const id = e?.detail?.tabId || ''
      if (!props.tabId || !id) return
      if (id === props.tabId) {
        reactivatedAt = Date.now()
        reactBuf = ''
        if (reactBufTimer) { try { clearTimeout(reactBufTimer) } catch {} ; reactBufTimer = null }
        try { doFit() } catch {}
      }
    } catch {}
  }
  window.addEventListener('tab-activated', onTabActive)
  wrap.value.__onTabActive = onTabActive

  const onKeyDown = (e) => {
    try {
      const isCtrl = !!e.ctrlKey
      const isAlt = !!e.altKey
      const isBracketRight = (e.key === ']' || e.code === 'BracketRight')
      if (isCtrl && isAlt && isBracketRight) {
        e.preventDefault()
        try { ws && ws.close() } catch {}
        try { window.dispatchEvent(new CustomEvent('webssh-exit', { detail: { tabId: props.tabId || '' } })) } catch {}
        try { term?.write("\r\n[Disconnected by Ctrl+Alt+]]\r\n") } catch {}
      }
    } catch {}
  }
  window.addEventListener('keydown', onKeyDown)
  wrap.value.__onKeyDown = onKeyDown
})

onBeforeUnmount(() => {
  try { wrap.value?.__ro?.disconnect() } catch {}
  try { window.removeEventListener('tab-activated', wrap.value?.__onTabActive) } catch {}
  try { window.removeEventListener('keydown', wrap.value?.__onKeyDown) } catch {}
  try { window.removeEventListener('dv-fontscale-change', wrap.value?.__onFontScale) } catch {}
  try { if (reactBufTimer) { clearTimeout(reactBufTimer); reactBufTimer = null } } catch {}
  try { if (pendingPromptTimer) { clearTimeout(pendingPromptTimer); pendingPromptTimer = null } } catch {}
  try { ws && ws.close() } catch {}
  try { term?.dispose() } catch {}
})
</script>

<style scoped>
.webssh { width: 100%; height: 100%; background: #0b1021; border-radius: 8px; border: 1px solid #1f2937; overflow: hidden; }
.term { width: 100%; height: 100%; }
/* 让 xterm 占满容器 */
.term :deep(.xterm) { width: 100% !important; height: 100% !important; }
</style>
