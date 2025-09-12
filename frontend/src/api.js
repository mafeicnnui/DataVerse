import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export default {
  get: (path, config) => api.get(path, config),
  post: (path, data, config) => api.post(path, data, config),
  put: (path, data, config) => api.put(path, data, config),
  delete: (path, config) => api.delete(path, config),
}
