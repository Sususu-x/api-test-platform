import request from './request'

export const generateCases = (description) => {
  return request.post('/ai/generate-cases', { description })
}
