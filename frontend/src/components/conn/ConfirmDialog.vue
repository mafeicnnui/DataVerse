<template>
  <div v-if="visible" class="modal-backdrop" @click.self="$emit('cancel')">
    <div class="modal confirm-modal">
      <div class="modal-header warn">
        <h2 class="with-icon">
          <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M1 21h22L12 2 1 21zm12-3h-2v2h2v-2zm0-8h-2v6h2V10z"/></svg>
          删除确认
        </h2>
      </div>
      <div class="modal-body">
        <div class="confirm-content">
          <p class="confirm-text">{{ text }}</p>
          <p class="confirm-subtext">
            类型：{{ meta?.type || '-' }} ｜ 环境：{{ meta?.env || '-' }}
          </p>
        </div>
      </div>
      <div class="actions modal-actions">
        <button class="icon-btn warn" @click="$emit('confirm')" title="确认删除" aria-label="确认删除">
          <!-- 精致垃圾桶图标：分体桶身 + 盖子，与列表按钮统一 -->
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true">
            <!-- 盖子 -->
            <path d="M9 4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2h4v2H5V4h4zm2 0a0 0 0 0 0 0 0h2a0 0 0 0 0 0 0H11z"/>
            <!-- 桶身 -->
            <path d="M6 8h12l-1 12a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L6 8zM10 11v8h2v-8h-2zm4 0v8h2v-8h-2zM8 11v8h2v-8H8z"/>
          </svg>
        </button>
        <button class="icon-btn" @click="$emit('cancel')" title="取消" aria-label="取消">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true">
            <path d="M18.3 5.71 12 12.01 5.7 5.7 4.29 7.11 10.59 13.4 4.29 19.7 5.7 21.11 12 14.81 18.3 21.11 19.71 19.7 13.41 13.4 19.71 7.11z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  visible: { type: Boolean, default: false },
  text: { type: String, default: '' },
  meta: { type: Object, default: () => ({}) }
})
const emit = defineEmits(['confirm','cancel'])
</script>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index: 2000; }
.modal { width: 520px; max-width: 90vw; background: #fff; border-radius: 10px; box-shadow: 0 12px 32px rgba(0,0,0,0.22); overflow: hidden; }
.modal-header { padding: 12px 16px; border-bottom: 1px solid #eee; }
.modal-header.warn { background: #fff7f7; }
.modal-header .with-icon { display:flex; gap:8px; align-items:center; }
.modal-body { padding: 12px 16px; }
.actions { margin-top: 12px; display: flex; gap: 8px; justify-content: flex-end; padding: 0 16px 16px; }
/* 按钮样式统一迁移至全局 style.css 的 .icon-btn 系列，这里不再定义，避免 scoped 覆盖全局样式 */
.confirm-text { font-size: 14px; color: #111; margin: 0 0 4px; }
.confirm-subtext { font-size: 13px; color: #666; margin: 0; }
</style>
