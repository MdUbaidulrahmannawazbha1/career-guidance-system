import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { AuthContext } from './authContextInstance'
import api, { setAuthTokenGetter, setUnauthorizedHandler } from '../services/api'

const getExpiryFromToken = (token) => {
  if (!token) {
    return null
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp ? payload.exp * 1000 : null
  } catch {
    return null
  }
}


export function AuthProvider({ children }) {
  const [authState, setAuthState] = useState({
    token: null,
    user_id: null,
    role: null,
    full_name: null,
  })
  const refreshTimerRef = useRef(null)

  const clearRefreshTimer = useCallback(() => {
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current)
      refreshTimerRef.current = null
    }
  }, [])

  const logout = useCallback(() => {
    clearRefreshTimer()
    setAuthState({ token: null, user_id: null, role: null, full_name: null })
  }, [clearRefreshTimer])

  const scheduleRefresh = useCallback(
    (token) => {
      clearRefreshTimer()
      const expiry = getExpiryFromToken(token)

      if (!expiry) {
        return
      }

      const refreshAt = expiry - 5 * 60 * 1000
      const delay = refreshAt - Date.now()

      refreshTimerRef.current = setTimeout(async () => {
        try {
          const { data } = await api.post('/auth/refresh', {}, { headers: { 'X-Skip-Auth': 'true' } })
          if (data?.token) {
            setAuthState((prev) => ({
              ...prev,
              token: data.token,
              user_id: data.user_id ?? prev.user_id,
              role: data.role ?? prev.role,
              full_name: data.full_name ?? prev.full_name,
            }))
          }
        } catch {
          logout()
        }
      }, Math.max(delay, 0))
    },
    [clearRefreshTimer, logout],
  )

  const login = useCallback(
    (session) => {
      setAuthState({
        token: session.token,
        user_id: session.user_id,
        role: session.role,
        full_name: session.full_name,
      })
      scheduleRefresh(session.token)
    },
    [scheduleRefresh],
  )

  const isAuthenticated = useCallback(() => {
    if (!authState.token) {
      return false
    }

    const expiry = getExpiryFromToken(authState.token)
    return !expiry || expiry > Date.now()
  }, [authState.token])

  useEffect(() => {
    setAuthTokenGetter(() => authState.token)
    setUnauthorizedHandler(() => {
      logout()
      window.location.href = '/login'
    })
  }, [authState.token, logout])

  useEffect(() => {
    if (authState.token) {
      scheduleRefresh(authState.token)
      return
    }

    clearRefreshTimer()
  }, [authState.token, scheduleRefresh, clearRefreshTimer])

  useEffect(() => () => clearRefreshTimer(), [clearRefreshTimer])

  const value = useMemo(
    () => ({ ...authState, login, logout, isAuthenticated }),
    [authState, login, logout, isAuthenticated],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
