import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const STORAGE_KEY = 'shopsmart:user'
const AuthContext = createContext()

function buildUser({ name, email }) {
  if (name && name.trim()) return { name: name.trim(), email }
  const fallbackName = email ? email.split('@')[0] : 'ShopSmart User'
  return { name: fallbackName, email }
}

export function AuthProvider({ children }) {
  const navigate = useNavigate()
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  })

  const isAuthenticated = Boolean(user)

  useEffect(() => {
    if (user) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }, [user])

  const login = (email, password) => {
    if (!email || !password) return
    const authUser = buildUser({ name: '', email })
    setUser(authUser)
    navigate('/app')
  }

  const signup = (name, email, password) => {
    if (!email || !password) return
    const authUser = buildUser({ name, email })
    setUser(authUser)
    navigate('/app')
  }

  const logout = () => {
    setUser(null)
    navigate('/')
  }

  const value = useMemo(
    () => ({ user, isAuthenticated, login, signup, logout }),
    [user, isAuthenticated],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
