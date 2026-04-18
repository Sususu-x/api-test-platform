import axios from 'axios'

const request = axios.create({
  baseURL: '/api',   // 关键：相对路径，由 Nginx 代理到后端
  timeout: 30000
})

// 请求拦截器（可在此添加 token）
request.interceptors.request.use(config => {
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器
request.interceptors.response.use(response => {
  return response.data
}, error => {
  console.error('API Error:', error)
  return Promise.reject(error)
})

export default request
