<template>
  <div class="app-container">
    <h1>🚀 API自动化测试平台</h1>

    <el-card class="action-card">
      <el-button type="primary" @click="dialogVisible = true">➕ 新增用例</el-button>
      <el-button type="success" @click="executeBatch">▶️ 批量执行选中</el-button>
      <el-button type="info" @click="openReport">📊 查看测试报告</el-button>
    </el-card>
    <div style="display: flex; align-items: center; gap: 10px;">
  <el-select v-model="activeEnvId" placeholder="选择环境" @change="switchEnv" style="width: 180px;">
    <el-option v-for="env in envList" :key="env.id" :label="env.name" :value="env.id">
      <span>{{ env.name }}</span>
      <span v-if="env.is_active" style="color: #67C23A; margin-left: 5px;">(当前)</span>
    </el-option>
  </el-select>
  <el-button @click="envDialogVisible = true; resetEnvForm()">⚙️ 环境配置</el-button>
</div>
    <el-table
      :data="caseList"
      @selection-change="handleSelectionChange"
      v-loading="loading"
      border
    >
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="用例名称" min-width="150"></el-table-column>
      <el-table-column prop="url" label="请求URL" min-width="250"></el-table-column>
      <el-table-column prop="method" label="方法" width="100">
        <template #default="{ row }">
          <el-tag :type="getMethodTagType(row.method)">{{ row.method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="expected_status" label="期望状态码" width="120"></el-table-column>
      <el-table-column prop="assert_type" label="断言类型" width="120">
  <template #default="{ row }">
    <el-tag size="small">{{ row.assert_type }}</el-tag>
  </template>
</el-table-column>
      <el-table-column label="操作" width="150">
  <template #default="{ row }">
    <el-button type="primary" size="small" @click="editCase(row)">编辑</el-button>
  </template>
</el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="新增测试用例" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="用例名称">
          <el-input v-model="form.name" placeholder="例如: 获取文章1"></el-input>
        </el-form-item>
        <el-form-item label="请求URL">
          <el-input v-model="form.url" placeholder="完整地址，如 https://jsonplaceholder.typicode.com/posts/1"></el-input>
        </el-form-item>
        <el-form-item label="请求方法">
          <el-select v-model="form.method" placeholder="请选择">
            <el-option label="GET" value="GET"></el-option>
            <el-option label="POST" value="POST"></el-option>
            <el-option label="PUT" value="PUT"></el-option>
            <el-option label="DELETE" value="DELETE"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="断言类型">
  <el-select v-model="form.assert_type" placeholder="请选择断言类型">
    <el-option label="包含关键词" value="contains"></el-option>
    <el-option label="JSONPath" value="jsonpath"></el-option>
    <el-option label="正则表达式" value="regex"></el-option>
  </el-select>
</el-form-item>

<!-- 当断言类型为 contains 时，显示“期望响应包含” -->
<el-form-item label="期望响应包含" v-if="form.assert_type === 'contains'">
  <el-input v-model="form.expected_response" placeholder="例如: userId"></el-input>
</el-form-item>

<!-- 当断言类型为 jsonpath 或 regex 时，显示“断言目标” -->
<el-form-item label="断言目标" v-if="form.assert_type === 'jsonpath' || form.assert_type === 'regex'">
  <el-input v-model="form.assert_target" :placeholder="form.assert_type === 'jsonpath' ? '例如: $.userId' : '例如: \\d{6}'"></el-input>
</el-form-item>

<!-- 当断言类型为 jsonpath 时，显示“期望值” -->
<el-form-item label="期望值" v-if="form.assert_type === 'jsonpath'">
  <el-input v-model="form.expected_value" placeholder="例如: 1"></el-input>
</el-form-item>

<!-- 原有的期望状态码 -->
<el-form-item label="期望状态码">
  <el-input-number v-model="form.expected_status" :min="100" :max="599"></el-input-number>
</el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false; resetForm()">取消</el-button>
        <el-button type="primary" @click="createCase">确定</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="envDialogVisible" title="环境配置" width="700px">
  <el-table :data="envList" style="margin-bottom: 20px;">
    <el-table-column prop="name" label="名称"></el-table-column>
    <el-table-column prop="base_url" label="Base URL"></el-table-column>
    <el-table-column label="激活" width="80">
      <template #default="{ row }">
        <el-tag v-if="row.is_active" type="success">激活</el-tag>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="150">
      <template #default="{ row }">
        <el-button type="primary" size="small" @click="editEnv(row)">编辑</el-button>
        <el-button type="danger" size="small" @click="deleteEnv(row)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>

  <el-divider>添加 / 编辑环境</el-divider>

  <el-form :model="envForm" label-width="100px">
    <el-form-item label="环境名称">
      <el-input v-model="envForm.name" placeholder="如：开发环境"></el-input>
    </el-form-item>
    <el-form-item label="Base URL">
      <el-input v-model="envForm.base_url" placeholder="如 https://api.example.com"></el-input>
    </el-form-item>
    <el-form-item label="全局请求头">
      <el-input v-model="envForm.global_headers" type="textarea" :rows="3" placeholder='JSON格式，如 {"Authorization": "Bearer xxx"}'></el-input>
    </el-form-item>
    <el-form-item label="设为激活">
      <el-switch v-model="envForm.is_active"></el-switch>
    </el-form-item>
  </el-form>
  <template #footer>
    <el-button @click="envDialogVisible = false">取消</el-button>
    <el-button type="primary" @click="saveEnvironment">保存</el-button>
  </template>
</el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getCases, createCase as apiCreateCase, executeBatch as apiExecuteBatch } from './api/case'
import { getEnvironments, createEnvironment, updateEnvironment, deleteEnvironment, activateEnvironment } from './api/environment'

const caseList = ref([])
const loading = ref(false)
const selectedCases = ref([])

const dialogVisible = ref(false)
const form = reactive({
  id: null,
  name: '',
  url: '',
  method: 'GET',
  expected_status: 200,
  expected_response: '',      // 用于 contains 类型的关键词
  expected_value: ''          // 用于 jsonpath 的比对值
})
const envList = ref([])
const activeEnvId = ref(null)
const envDialogVisible = ref(false)
const envForm = reactive({
  id: null,
  name: '',
  base_url: '',
  global_headers: '',
  is_active: false
})

const fetchCases = async () => {
  loading.value = true
  try {
    caseList.value = await getCases()
  } catch (error) {
    ElMessage.error('获取用例列表失败')
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (val) => {
  selectedCases.value = val
}

const getMethodTagType = (method) => {
  const types = { GET: 'success', POST: 'warning', PUT: '', DELETE: 'danger' }
  return types[method] || 'info'
}

const resetForm = () => {
  Object.assign(form, {
    name: '',
    url: '',
    method: 'GET',
    assert_type: 'contains',
    assert_target: '',
    expected_status: 200,
    expected_response: '',
    expected_value: ''
  })
}

const createCase = async () => {
  // 构建要发送的数据对象
  const payload = {
    name: form.name,
    url: form.url,
    method: form.method,
    expected_status: form.expected_status,
    assert_type: form.assert_type,
    assert_target: form.assert_type !== 'contains' ? form.assert_target : null,
    expected_response: ''  // 最终传给后端的 expected_response
  }

  // 根据断言类型处理 expected_response 的值
  if (form.assert_type === 'contains') {
    payload.expected_response = form.expected_response
  } else if (form.assert_type === 'jsonpath') {
    payload.expected_response = form.expected_value  // 将期望值赋给 expected_response
  } else if (form.assert_type === 'regex') {
    payload.expected_response = form.assert_target   // 正则表达式本身作为断言内容
  }

  // 处理请求头和请求体（如果后续需要可扩展，此处先设为 null）
  payload.headers = null
  payload.request_body = null

  try {
    await apiCreateCase(payload)
    ElMessage.success('用例创建成功！')
    dialogVisible.value = false
    resetForm()
    fetchCases()
  } catch (error) {
    ElMessage.error('创建用例失败')
  }
}

const editCase = (row) => {
  Object.assign(form, {
    id: row.id,
    name: row.name,
    url: row.url,
    method: row.method,
    assert_type: row.assert_type,
    assert_target: row.assert_target,
    expected_status: row.expected_status,
    expected_response: row.expected_response,
    expected_value: row.assert_type === 'jsonpath' ? row.expected_response : ''
  })
  dialogVisible.value = true
}

const saveCase = async () => {
  const payload = {
    name: form.name,
    url: form.url,
    method: form.method,
    expected_status: form.expected_status,
    assert_type: form.assert_type,
    assert_target: form.assert_type !== 'contains' ? form.assert_target : null,
    expected_response: ''
  }

  if (form.assert_type === 'contains') {
    payload.expected_response = form.expected_response
  } else if (form.assert_type === 'jsonpath') {
    payload.expected_response = form.expected_value
  } else if (form.assert_type === 'regex') {
    payload.expected_response = form.assert_target
  }

  try {
    if (form.id) {
      await updateCase(form.id, payload)
      ElMessage.success('用例更新成功')
    } else {
      await apiCreateCase(payload)
      ElMessage.success('用例创建成功')
    }
    dialogVisible.value = false
    resetForm()
    fetchCases()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const executeBatch = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择要执行的用例')
    return
  }
  const ids = selectedCases.value.map(item => item.id)
  try {
    await apiExecuteBatch(ids)
    ElMessage.success('批量执行任务已提交，稍后可在报告中查看结果')
    // 延迟15秒后打开报告（根据实际用例数量调整）
    setTimeout(() => {
      // 加上随机参数强制刷新
      window.open(`http://localhost:8000/allure-report/?v=${Date.now()}`, '_blank')
    }, 15000)
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

const openReport = () => {
  window.open('http://localhost:8000/allure-report/', '_blank')
}

const fetchEnvironments = async () => {
  try {
    envList.value = await getEnvironments()
    const activeEnv = envList.value.find(e => e.is_active)
    if (activeEnv) activeEnvId.value = activeEnv.id
  } catch (error) {
    ElMessage.error('获取环境列表失败')
  }
}

const switchEnv = async (envId) => {
  try {
    await activateEnvironment(envId)
    ElMessage.success('环境已切换')
    fetchEnvironments()
  } catch (error) {
    ElMessage.error('切换失败')
  }
}

const saveEnvironment = async () => {
  const payload = {
    name: envForm.name,
    base_url: envForm.base_url,
    global_headers: envForm.global_headers,
    is_active: envForm.is_active
  }
  try {
    if (envForm.id) {
      await updateEnvironment(envForm.id, payload)
    } else {
      await createEnvironment(payload)
    }
    ElMessage.success('保存成功')
    envDialogVisible.value = false
    fetchEnvironments()
    resetEnvForm()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const resetEnvForm = () => {
  Object.assign(envForm, {
    id: null,
    name: '',
    base_url: '',
    global_headers: '',
    is_active: false
  })
}

const editEnv = (env) => {
  Object.assign(envForm, {
    id: env.id,
    name: env.name,
    base_url: env.base_url,
    global_headers: env.global_headers,
    is_active: env.is_active
  })
}

const deleteEnv = async (env) => {
  try {
    await ElMessageBox.confirm('确定删除该环境吗？', '提示', { type: 'warning' })
    await deleteEnvironment(env.id)
    ElMessage.success('删除成功')
    fetchEnvironments()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchCases(), fetchEnvironments()
})
</script>

<style scoped>
.app-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}
.action-card {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
</style>
