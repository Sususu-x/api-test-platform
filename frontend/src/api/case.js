import request from './request'

// 获取用例列表
export const getCases = (params) => {
  return request.get('/api/cases/', { params })
}

// 创建新用例
export const createCase = (data) => {
  return request.post('/api/cases/', data)
}

// 批量执行用例
export const executeBatch = (caseIds) => {
  return request.post('/api/cases/execute-batch', caseIds)
}