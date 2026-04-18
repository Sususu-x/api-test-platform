import request from './request'

export const getEnvironments = () => request.get('environments/')
export const createEnvironment = (data) => request.post('environments/', data)
export const updateEnvironment = (id, data) => request.put(`environments/${id}`, data)
export const deleteEnvironment = (id) => request.delete(`environments/${id}`)
export const activateEnvironment = (id) => request.post(`environments/activate/${id}`)
export const getActiveEnvironment = () => request.get('environments/active')
