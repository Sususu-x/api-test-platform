import axios from 'axios'

const request = axios.create({
  baseURL: 'http://localhost:8000', // 后端地址
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