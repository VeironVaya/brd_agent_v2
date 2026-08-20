/**
 * AuthContext — single source of truth for the logged-in user.
 *
 * Responsibilities:
 *   1. On mount, validate the stored token against the server via
 *      GET /auth/session. This is the real auth check — not just
 *      "does a token string exist in localStorage?"
 *   2. Expose `user`, `loading`, `login()`, and `logout()` to all
 *      descendants so any component can react to auth state changes.
 *   3. Listen for the 'auth:expired' CustomEvent fired by api.js
 *      when any request returns 401 mid-session, and automatically
 *      clear state and redirect to /login.
 *
 * api.js stays a plain JS module with zero React imports — it
 * communicates the 401 signal via a native window CustomEvent,
 * which this context picks up and acts on.
 */

import { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import * as api from '../services/api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const navigate = useNavigate()
  // null  = not yet known (still loading)
  // false = known to be unauthenticated
  // obj   = the logged-in user { id, email, name }
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  // Guard against calling navigate() after unmount (StrictMode double-effect)
  const mounted = useRef(true)

  // --- Initial session validation ---
  useEffect(() => {
    mounted.current = true
    api.getSession().then((u) => {
      if (!mounted.current) return
      setUser(u ?? false)
      setLoading(false)
    })
    return () => {
      mounted.current = false
    }
  }, [])

  // --- 401 mid-session listener ---
  // api.js dispatches 'auth:expired' whenever any request gets a 401
  // back from the server (expired token, server-side revocation, etc.)
  useEffect(() => {
    function handleExpired() {
      if (!mounted.current) return
      setUser(false)
      navigate('/login', { replace: true })
    }
    window.addEventListener('auth:expired', handleExpired)
    return () => window.removeEventListener('auth:expired', handleExpired)
  }, [navigate])

  // --- login — called by LoginPage after api.login() resolves ---
  const login = useCallback((userData) => {
    setUser(userData)
  }, [])

  // --- logout — awaits server revocation then clears state ---
  const logout = useCallback(async () => {
    await api.logout() // revokes jti server-side, then clearToken()
    if (!mounted.current) return
    setUser(false)
    navigate('/login', { replace: true })
  }, [navigate])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

/** Convenience hook — throws if used outside <AuthProvider>. */
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (ctx === null) {
    throw new Error('useAuth must be used inside <AuthProvider>')
  }
  return ctx
}
