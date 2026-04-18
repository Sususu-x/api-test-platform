import request from './request'

// 修改前：request.get('/api/cases/')
// 修改后：request.get('cases/')
export const getCases = (params) => request.get('cases/', { params })
export const createCase = (data) => request.post('cases/', data)
export const updateCase = (id, data) => request.put(`cases/${id}/`, data)
export const executeBatch = (caseIds) => request.post('cases/execute-batch', caseIds)
