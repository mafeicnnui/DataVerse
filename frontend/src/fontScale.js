// Global font scaling utility for UI and monospace text.
// - Ctrl/Cmd + Wheel to adjust
// - Ctrl/Cmd + '+' / '-' to adjust, Ctrl/Cmd + '0' to reset
// - Persists to localStorage and exposes CSS vars:
//   --dv-font-ui, --dv-font-mono (px)

const STORAGE_KEY = 'dv_font_scale_v1'
const DEFAULTS = { ui: 14, mono: 13 }
const MIN = 10
const MAX = 24

function clamp(n) {
  if (!Number.isFinite(n)) return DEFAULTS.ui
  return Math.max(MIN, Math.min(MAX, Math.round(n)))
}

function readState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ui: DEFAULTS.ui, mono: DEFAULTS.mono }
    const data = JSON.parse(raw)
    const ui = clamp(Number(data.ui))
    const mono = clamp(Number(data.mono))
    if (!ui || !mono) throw new Error('invalid')
    return { ui, mono }
  } catch {
    return { ui: DEFAULTS.ui, mono: DEFAULTS.mono }
  }
}

function writeState(s) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(s)) } catch {}
}

function applyVars(uiPx, monoPx) {
  try {
    const root = document.documentElement
    root.style.setProperty('--dv-font-ui', `${uiPx}px`)
    root.style.setProperty('--dv-font-mono', `${monoPx}px`)
    // Expose for JS consumers
    window.__dv_font_ui_px = uiPx
    window.__dv_font_mono_px = monoPx
    // Broadcast
    window.dispatchEvent(new CustomEvent('dv-fontscale-change', { detail: { uiPx, monoPx } }))
  } catch {}
}

function currentVars() {
  try {
    const cs = getComputedStyle(document.documentElement)
    const u = parseFloat(cs.getPropertyValue('--dv-font-ui') || `${DEFAULTS.ui}`)
    const m = parseFloat(cs.getPropertyValue('--dv-font-mono') || `${DEFAULTS.mono}`)
    return { uiPx: clamp(u), monoPx: clamp(m) }
  } catch {
    return { uiPx: DEFAULTS.ui, monoPx: DEFAULTS.mono }
  }
}

function setScale(uiPx, monoPx) {
  const ui = clamp(uiPx)
  const mono = clamp(monoPx)
  writeState({ ui, mono })
  applyVars(ui, mono)
}

function step(delta) {
  const s = readState()
  const ui = clamp((s.ui || DEFAULTS.ui) + delta)
  const mono = clamp((s.mono || DEFAULTS.mono) + delta)
  writeState({ ui, mono })
  applyVars(ui, mono)
}

function reset() {
  writeState({ ...DEFAULTS })
  applyVars(DEFAULTS.ui, DEFAULTS.mono)
}

function handleWheel(e) {
  try {
    const mod = !!(e.ctrlKey || e.metaKey)
    if (!mod) return
    // Prevent browser page zoom/pinch-zoom default if possible
    try { e.preventDefault() } catch {}
    const delta = e.deltaY
    if (!Number.isFinite(delta) || delta === 0) return
    const dir = delta > 0 ? -1 : 1
    step(dir)
  } catch {}
}

function handleKeydown(e) {
  try {
    const mod = !!(e.ctrlKey || e.metaKey)
    if (!mod) return
    // Ctrl/Cmd + '=' or '+' => increase; '-' => decrease; '0' => reset
    const k = e.key
    if (k === '+' || k === '=') { e.preventDefault(); step(1) }
    else if (k === '-') { e.preventDefault(); step(-1) }
    else if (k === '0') { e.preventDefault(); reset() }
  } catch {}
}

export function initFontScaling() {
  // Initial apply from storage
  const s = readState()
  applyVars(clamp(s.ui), clamp(s.mono))
  // Bind listeners
  try { window.addEventListener('wheel', handleWheel, { passive: false }) } catch {}
  try { window.addEventListener('keydown', handleKeydown, { passive: false }) } catch {}
  // Expose helpers
  window.__dvFontScale = {
    get: () => ({ ...readState() }),
    set: setScale,
    reset,
    currentVars,
    step,
  }
}

// Optional: auto-init if imported late
if (typeof window !== 'undefined') {
  // Delay a tick to ensure documentElement exists
  setTimeout(() => {
    try {
      const cs = getComputedStyle(document.documentElement)
      const hasVar = !!cs
      if (hasVar) {
        // Avoid double-binding if already initialized
        if (!(window.__dv_fontscale_inited)) {
          window.__dv_fontscale_inited = true
          initFontScaling()
        }
      }
    } catch {}
  }, 0)
}


