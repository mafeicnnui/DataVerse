<template>
  <div class="console-bubbles">
    <div v-for="(b,i) in bubbles" :key="b.id" class="console-bubble" :style="{ bottom: (16 + i*56) + 'px' }">
      <span class="icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="12" rx="2" ry="2"/>
          <path d="M7 20h10"/>
        </svg>
      </span>
      <span class="txt" :title="b.title || '控制台'">{{ b.title || '控制台' }}</span>
      <button class="act" @click="restore(b)">还原</button>
      <button class="x" @click="dismiss(b.id)" title="关闭">×</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const bubbles = ref([]) // {id,title,url,tabs,ts}

function pushBubble(payload){
  const item = {
    id: `${Date.now()}:${Math.random().toString(36).slice(2,8)}`,
    title: payload?.title || '控制台',
    url: payload?.url || '/view=console',
    tabs: Number(payload?.tabs||0) || 0,
    ts: Date.now(),
  }
  bubbles.value.unshift(item)
  if (bubbles.value.length > 3) bubbles.value = bubbles.value.slice(0,3)
}

function onMessage(ev){
  try{
    const data = ev?.data || {}
    if (data && data.type==='console-minimized'){
      pushBubble(data)
    }
  }catch{}
}

function restore(b){
  try{
    // BroadcastChannel 与命名窗口配合，优先找回已最小化窗口
    const beat = Number(localStorage.getItem('dv_console_alive') || '0')
    const alive = Date.now() - beat < 3500
    if (alive){
      try{
        const ch = new BroadcastChannel('dv_console')
        let acked = false
        const onAck = (ev)=>{ const d = ev?.data||{}; if (d && d.type==='restore-ack'){ acked = true } }
        ch.addEventListener('message', onAck)
        ch.postMessage({ type: 'restore' })
        setTimeout(()=>{
          try{ ch.removeEventListener('message', onAck); ch.close() }catch{}
          if (!acked){ try{ window.open(b.url, 'dv_console', 'popup') }catch{} }
          dismiss(b.id)
        }, 1200)
        return
      }catch{}
    }
    // 不活跃：直接新开
    try{ window.open(b.url, 'dv_console', 'popup') }catch{}
    dismiss(b.id)
  }catch{}
}
function dismiss(id){ bubbles.value = bubbles.value.filter(x=>x.id!==id) }

function pickupFromStorage(){
  try{
    const raw = localStorage.getItem('dv_console_bubble')
    if (!raw) return
    localStorage.removeItem('dv_console_bubble')
    const data = JSON.parse(raw)
    if (data && data.type==='console-minimized') pushBubble(data)
  }catch{}
}

onMounted(()=>{
  try{ window.addEventListener('message', onMessage) }catch{}
  pickupFromStorage()
  setTimeout(pickupFromStorage, 500)
})
onBeforeUnmount(()=>{ try{ window.removeEventListener('message', onMessage) }catch{} })
</script>

<style scoped>
.console-bubbles { position: fixed; right: 16px; z-index: 40000; pointer-events: none; }
.console-bubble { position: fixed; right: 16px; min-width: 180px; height: 48px; padding: 6px 10px; background:#0b1220; color:#e5e7eb; border:1px solid #1f2937; border-radius:10px; box-shadow:0 8px 24px rgba(0,0,0,.3); display:flex; align-items:center; gap:8px; pointer-events:auto; }
.console-bubble .txt{ max-width: 120px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.console-bubble .act{ margin-left:auto; height: 28px; padding: 0 10px; border:1px solid #334155; border-radius:6px; background:#1d4ed8; color:#fff; cursor:pointer; }
.console-bubble .act:hover{ background:#1b46c6; }
.console-bubble .x{ width:22px; height:22px; border:1px solid #334155; border-radius:6px; background:#0b1220; color:#e5e7eb; cursor:pointer; }
.console-bubble .x:hover{ background:#0f172a; }
</style>
