import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authService } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('user')
    const token = localStorage.getItem('token')
    if (stored && token) setUser(JSON.parse(stored))
    setLoading(false)
  }, [])

  // identifier = username OR email (both work for login)
  const login = useCallback(async (identifier, password) => {
    const data = await authService.login(identifier, password)
    localStorage.setItem('token', data.access_token)
    const userObj = { username: identifier }
    localStorage.setItem('user', JSON.stringify(userObj))
    setUser(userObj)
    return data
  }, [])

  // Register requires all three fields
  const register = useCallback(async (username, email, password) => {
    return await authService.register(username, email, password)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
