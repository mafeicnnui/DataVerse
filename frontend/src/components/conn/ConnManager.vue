<template>
  <div class="container">

    <!-- 无障碍提示（离屏） -->
    <p v-if="message" class="offscreen" role="status" aria-live="polite">{{ message }}</p>

    <!-- 新增/编辑 弹窗 -->
    <ConnFormModal
      :visible="showModal"
      :dict-type="dictType"
      :dict-env="dictEnv"
      :dict-status="dictStatus"
      :editing="editing"
      v-model="form"
      :form-key="formKey"
      @submit="onSubmit"
      @close="closeModal"
    />

    <!-- 删除确认 弹窗 -->
    <ConfirmDialog
      :visible="confirmVisible"
      :text="confirmText"
      :meta="{ type: labelOf(dictType, confirmItem?.db_type), env: labelOf(dictEnv, confirmItem?.db_env) }"
      @confirm="performDelete"
      @cancel="cancelConfirm"
    />

    <!-- 筛选工具条（直接使用组件自身的 card 样式） -->
    <ConnToolbar
      :filter="filter"
      @update:filter="val => { Object.assign(filter, val || {}); page.value = 1 }"
      :dict-type="dictType"
      :dict-env="dictEnv"
      :dict-status="dictStatus"
      @query="onQuery"
      @create="onCreateNew"
    />

    <!-- 列表表格（直接使用组件自身卡片样式，避免外层 padding 导致宽度不一致） -->
    <ConnTable
      :items="pagedList"
      :dict-type="dictType"
      :dict-env="dictEnv"
      :dict-status="dictStatus"
      :page="page"
      :page-size="pageSize"
      :total-pages="totalPages"
      :items-total="filteredList.length"
      @edit="onEdit"
      @delete="onDelete"
      @test="onTest"
      @console="onConsole"
      @prev="prevPage"
      @next="nextPage"
      @update:page-size="val => { pageSize.value = val; page.value = 1 }"
    />

    <div class="notice" v-if="message">{{ message }}</div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../../api'
import ConnToolbar from './ConnToolbar.vue'
import ConnTable from './ConnTable.vue'
import ConnFormModal from './ConnFormModal.vue'
import ConfirmDialog from './ConfirmDialog.vue'

// 列表与筛选
const list = ref([])
const filter = reactive({ type: '', env: '', status: '' })
const page = ref(1)
const pageSize = ref(10)
const totalPages = computed(() => Math.max(1, Math.ceil((filteredList.value.length || 0) / pageSize.value)))
const pagedList = computed(() => {
  const arr = filteredList.value
  const start = (page.value - 1) * pageSize.value
  return arr.slice(start, start + pageSize.value)
})
function prevPage() { if (page.value > 1) page.value-- }
function nextPage() { if (page.value < totalPages.value) page.value++ }

// 字典
const dictType = ref([])
const dictEnv = ref([])
const dictStatus = ref([])

// 表单与弹窗
const showModal = ref(false)
const editing = ref(false)
const editingId = ref(null)
const formKey = ref(1)
const form = reactive({
  ip: '', port: '', user: '', password: '',
  db_type: '', db_env: '', status: '1', description: ''
})
const message = ref('')

function resetForm() {
  editing.value = false
  editingId.value = null
  form.ip = ''
  form.port = ''
  form.user = ''
  form.password = ''
  form.db_type = ''
  form.db_env = ''
  form.status = '1'
  form.description = ''
}

function onCreateNew() {
  resetForm()
  message.value = ''
  formKey.value++
  showModal.value = true
}
function closeModal() {
  showModal.value = false
  resetForm()
}

// 删除确认
const confirmVisible = ref(false)
const confirmText = ref('')
const confirmItem = ref(null)
function cancelConfirm() {
  confirmVisible.value = false
  confirmItem.value = null
  confirmText.value = ''
}

// API
async function fetchList() {
  try {
    const { data } = await api.get('/connections')
    list.value = data
    page.value = 1
  } catch (e) {
    message.value = '加载失败: ' + (e?.response?.data?.detail || e.message)
  }
}
function onQuery() { fetchList() }

async function fetchDicts() {
  try {
    const [t, e, s] = await Promise.all([
      api.get('/dicts/01'),
      api.get('/dicts/02'),
      api.get('/dicts/03'),
    ])
    dictType.value = t.data
    dictEnv.value = e.data
    dictStatus.value = s.data
  } catch (err) {
    message.value = '加载字典失败: ' + (err?.response?.data?.detail || err.message)
  }
}

function labelOf(arrRef, value) {
  const arr = Array.isArray(arrRef) ? arrRef : arrRef?.value
  const f = (arr || []).find(i => i.dmm === (value ?? ''))
  return f?.dmmc || value || ''
}

async function onSubmit() {
  try {
    if (!form.ip) return (message.value = '请填写数据库IP')
    if (!form.port) return (message.value = '请填写数据库端口')
    if (!form.user) return (message.value = '请填写用户名')
    if (!editing.value && !form.password) return (message.value = '请填写密码')
    if (!form.db_type) return (message.value = '请选择类型')
    if (!form.db_env) return (message.value = '请选择环境')
    if (!form.status) return (message.value = '请选择状态')

    if (editing.value && editingId.value) {
      const payload = { ...form }
      if (!payload.password || String(payload.password).trim() === '') delete payload.password
      const { data } = await api.put(`/connections/${editingId.value}`, payload)
      message.value = `已保存 #${data.id}`
    } else {
      const { data } = await api.post('/connections', { ...form })
      message.value = `已创建 #${data.id}`
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
  form.ip = item.ip
  form.port = item.port
  form.user = item.user
  form.password = ''
  form.db_type = item.db_type || ''
  form.db_env = item.db_env || ''
  form.status = item.status || '1'
  form.description = item.description || ''
  showModal.value = true
}

function onDelete(item) {
  confirmItem.value = item
  const fallback = `${item.ip}:${item.port} (#${item.id})`
  const label = (item.description && item.description.trim()) ? item.description.trim() : fallback
  confirmText.value = `确定要删除 “${label}” 吗？`
  confirmVisible.value = true
}

async function performDelete() {
  const item = confirmItem.value
  if (!item) return cancelConfirm()
  try {
    await api.delete(`/connections/${item.id}`)
    message.value = `已删除 #${item.id}`
    await fetchList()
  } catch (e) {
    message.value = '删除失败: ' + (e?.response?.data?.detail || e.message)
  } finally {
    cancelConfirm()
  }
}

async function onTest(item) {
  try {
    const { data } = await api.post(`/connections/${item.id}/test`)
    message.value = `测试结果: ${data.success ? '成功' : '失败'}`
  } catch (e) {
    message.value = '测试失败: ' + (e?.response?.data?.detail || e.message)
  }
}

function onConsole(item) {
  // 预留：与“工单查询”联动（可将 item.id 写入全局/本地存储，或发出全局事件供 App.vue 捕获）
  try {
    const label = `${item.ip}:${item.port}`
    message.value = `准备打开控制台: ${label}`
    // 示例：设置一个全局提示或本地存储，后续在 App.vue 中对接打开工单查询并选中连接
    localStorage.setItem('pending_console_conn_id', String(item.id))
    window.dispatchEvent(new CustomEvent('dv:open-console', { detail: { connId: item.id } }))
  } catch {}
}

const filteredList = computed(() => {
  return (list.value || []).filter(it => {
    if (filter.type && it.db_type !== filter.type) return false
    if (filter.env && it.db_env !== filter.env) return false
    if (filter.status && it.status !== filter.status) return false
    return true
  })
})

onMounted(async () => {
  await fetchDicts()
  await fetchList()
  // 清空一次，覆盖浏览器自动填充
  resetForm(); formKey.value++
  await Promise.resolve()
  resetForm(); formKey.value++
  setTimeout(() => { resetForm(); formKey.value++ }, 300)
})
</script>

<style scoped>
.container { width: 100%; max-width: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px; }
/* 兼容旧样式占位，不再添加额外的外边距/内边距，防止宽度与间距不一致 */
.card { background: transparent; border: none; border-radius: 10px; box-shadow: none; }
.card--frameless { background: transparent !important; border: none !important; box-shadow: none !important; }
.section-block { padding: 0; margin: 0; }
.notice { margin-top: 12px; color: #555; }
.offscreen { position: absolute; left: -9999px; width: 0; height: 0; opacity: 0; pointer-events: none; }
</style>
