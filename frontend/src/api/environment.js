import request from './request'

export const getEnvironments = () => request.get('/api/environments/')
export const createEnvironment = (data) => request.post('/api/environments/', data)
export const updateEnvironment = (id, data) => request.put(`/api/environments/${id}`, data)
export const deleteEnvironment = (id) => request.delete(`/api/environments/${id}`)
export const activateEnvironment = (id) => request.post(`/api/environments/activate/${id}`)
export const getActiveEnvironment = () => request.get('/api/environments/active')
