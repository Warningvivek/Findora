import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally — clear token and redirect
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/auth'
    }
    return Promise.reject(err)
  }
)

// ─── Auth ────────────────────────────────────────────────────────────────────

export const authService = {
  async register(username, email, password) {
  const res = await api.post('/api/auth/register', {
    username,
    email,
    password,
  })
  return res.data
  },

  async login(username, password) {
  const res = await api.post('/api/auth/login', {
    username,
    password,
  })
  return res.data
  },
}

// ─── Memories ────────────────────────────────────────────────────────────────

export const memoriesService = {
  async getAll(params = {}) {
    const res = await api.get('/api/memories', { params })
    return res.data
  },

  async create(formData) {
  const res = await api.post('/api/memories/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
  },
  async createNote(data) {
  const res = await api.post('/api/memories/notes', data)
  return res.data
  },

  async toggleFavorite(id) {
    const res = await api.patch(`/api/memories/${id}/favorite`)
    return res.data
  },

  async delete(id) {
    const res = await api.delete(`/api/memories/${id}`)
    return res.data
  },
}

// ─── Search ──────────────────────────────────────────────────────────────────

export const searchService = {
  async search(query, options = {}) {
    const res = await api.get('/api/search', {
      params: { q: query, ...options },
    })
    return res.data // { results, summary, search_history_id }
  },
}

export default api
