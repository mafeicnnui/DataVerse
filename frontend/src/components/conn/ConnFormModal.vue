<template>
  <div v-if="visible" class="modal-backdrop">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ editing ? '编辑连接' : '新增连接' }}</h2>
      </div>
      <form @submit.prevent="onSubmitLocal" :key="formKey" autocomplete="off" class="modal-body">
        <!-- 防自动填充诱饵字段 -->
        <input class="offscreen" type="text" autocomplete="username" tabindex="-1" aria-hidden="true" />
        <input class="offscreen" type="password" autocomplete="current-password" tabindex="-1" aria-hidden="true" />
        <div class="grid">
          <label>
            数据库IP
            <input v-model="localForm.ip" name="ip_new" placeholder="请输入数据库IP" required autocomplete="off ip-new" autocapitalize="off" autocorrect="off" spellcheck="false" readonly="true" @focus="e => e.target.removeAttribute('readonly')" />
          </label>
          <label>
            数据库端口
            <input v-model="localForm.port" name="port_new" placeholder="请输入数据库端口" required autocomplete="off port-new" autocapitalize="off" autocorrect="off" spellcheck="false" readonly="true" @focus="e => e.target.removeAttribute('readonly')" />
          </label>
          <label>
            用户名
            <input v-model="localForm.user" :name="'user_'+formKey" placeholder="请输入用户名" required autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" readonly="true" @focus="e => e.target.removeAttribute('readonly')" />
          </label>
          <label>
            密码
            <input
              v-model="localForm.password"
              :name="'pass_'+formKey"
              type="text"
              class="mask-password"
              placeholder="请输入密码"
              :required="!editing"
              autocomplete="off"
              autocapitalize="off"
              autocorrect="off"
              spellcheck="false"
              data-lpignore="true"
              data-1p-ignore
              data-bwignore
              readonly="true"
              @focus="e => e.target.removeAttribute('readonly')"
            />
            <small class="field-hint" aria-live="polite">{{ editing ? '留空表示不修改原密码' : '新增必须填写密码' }}</small>
          </label>
          <label>
            类型
            <select v-model="localForm.db_type">
              <option value="">请选择</option>
              <option v-for="opt in dictType" :key="opt.dmm" :value="opt.dmm">{{ opt.dmmc }}</option>
            </select>
          </label>
          <label>
            环境
            <select v-model="localForm.db_env">
              <option value="">请选择</option>
              <option v-for="opt in dictEnv" :key="opt.dmm" :value="opt.dmm">{{ opt.dmmc }}</option>
            </select>
          </label>
          <label>
            状态
            <select v-model="localForm.status">
              <option value="">请选择</option>
              <option v-for="opt in dictStatus" :key="opt.dmm" :value="opt.dmm">{{ opt.dmmc }}</option>
            </select>
          </label>
          <label>
            描述
            <input v-model="localForm.description" placeholder="描述" readonly="true" @focus="e => e.target.removeAttribute('readonly')" />
          </label>
        </div>
        <div class="actions modal-actions">
          <button type="button" class="icon-btn add" @click="onSubmitLocal" title="确认" aria-label="确认">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>
          </button>
          <button type="button" class="icon-btn" @click="$emit('close')" title="取消" aria-label="取消">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M18.3 5.71 12 12.01 5.7 5.7 4.29 7.11 10.59 13.4 4.29 19.7 5.7 21.11 12 14.81 18.3 21.11 19.71 19.7 13.41 13.4 19.71 7.11z"/></svg>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  dictType: { type: Array, default: () => [] },
  dictEnv: { type: Array, default: () => [] },
  dictStatus: { type: Array, default: () => [] },
  editing: { type: Boolean, default: false },
  formKey: { type: Number, default: 1 },
  modelValue: { type: Object, required: true }
})
const emit = defineEmits(['submit','close','update:modelValue'])

const localForm = reactive({
  ip: '', port: '', database: '', user: '', password: '',
  db_type: '', db_env: '', status: '1', description: ''
})

watch(() => props.modelValue, (v) => {
  Object.assign(localForm, v || {})
}, { immediate: true, deep: true })

function onSubmitLocal() {
  emit('update:modelValue', { ...localForm })
  emit('submit')
}
</script>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.35); display:flex; align-items:center; justify-content:center; z-index: 2000; }
.modal { width: 680px; max-width: 90vw; background: #fff; border-radius: 10px; box-shadow: 0 12px 32px rgba(0,0,0,0.22); overflow: hidden; }
.modal-header { padding: 12px 16px; border-bottom: 1px solid #e0e7ff; background: #f5f7ff; }
.modal-header h2 { margin: 0; font-size: 16px; line-height: 20px; font-weight: 600; color: #0b57d0; }
.modal-body { padding: 12px 16px; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.grid .span-2 { grid-column: span 2; }
label { display: flex; flex-direction: column; gap: 6px; font-size: 14px; }
input, select { padding: 6px 10px; height: 28px; line-height: 28px; border: 1px solid #dcdcdc; border-radius: 6px; font-size: 14px; }
.actions { margin-top: 12px; display: flex; gap: 8px; justify-content: flex-end; }
.icon-btn { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:6px; border:1px solid #c9c9c9; background:#fff; color:#333; cursor:pointer; }
.icon-btn.add { background:#e8f0fe; border-color:#3b82f6; color:#0b57d0; }
.icon-btn.add:hover { background:#dbe8ff; }
.offscreen { position: absolute; left: -9999px; width: 0; height: 0; opacity: 0; pointer-events: none; }
.mask-password { -webkit-text-security: disc; }
</style>
