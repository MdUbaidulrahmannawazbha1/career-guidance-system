import { useMemo, useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import api from '../../services/api'
import { roleDashboardPath, useAuth } from '../../context/AuthContext'

const demoUserByEmail = {
  'student@example.com': { role: 'student', user_id: 101, full_name: 'Student User' },
  'counsellor@example.com': { role: 'counsellor', user_id: 102, full_name: 'Counsellor User' },
  'mentor@example.com': { role: 'mentor', user_id: 103, full_name: 'Mentor User' },
  'admin@example.com': { role: 'admin', user_id: 104, full_name: 'Admin User' },
}

const createDummyJwt = (role) => {
  const payload = { role, exp: Math.floor(Date.now() / 1000) + 60 * 60 }
  return `header.${btoa(JSON.stringify(payload))}.signature`
}

export default function Login() {
  const auth = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('student@example.com')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const defaultRoute = useMemo(() => {
    if (auth.role && roleDashboardPath[auth.role]) {
      return roleDashboardPath[auth.role]
    }

    return '/student/dashboard'
  }, [auth.role])

  const redirectTo = location.state?.from?.pathname || defaultRoute

  if (auth.isAuthenticated()) {
    return <Navigate to={defaultRoute} replace />
  }

  const completeLogin = (session) => {
    auth.login(session)
    navigate(roleDashboardPath[session.role] || redirectTo, { replace: true })
  }

  const handleEmailLogin = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const { data } = await api.post('/auth/login', { email, password })
      if (!data?.token || !data?.role) {
        throw new Error('Invalid login response.')
      }
      completeLogin(data)
    } catch {
      const fallback = demoUserByEmail[email.trim().toLowerCase()]
      if (fallback && password) {
        completeLogin({ ...fallback, token: createDummyJwt(fallback.role) })
      } else {
        setError('Invalid credentials. Try a demo email and any password.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setError('')
    setLoading(true)

    try {
      const { data } = await api.get('/auth/google/callback')
      if (!data?.token || !data?.role) {
        throw new Error('OAuth failed')
      }
      completeLogin(data)
    } catch {
      completeLogin({
        token: createDummyJwt('student'),
        user_id: 201,
        role: 'student',
        full_name: 'Google Student',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-indigo-100 via-white to-cyan-100 px-4">
      <div className="w-full max-w-md rounded-2xl border border-white/60 bg-white/80 p-8 shadow-xl backdrop-blur">
        <h1 className="text-2xl font-semibold text-slate-900">Sign in</h1>
        <p className="mt-2 text-sm text-slate-600">Use your account to continue to your dashboard.</p>

        <form className="mt-6 space-y-4" onSubmit={handleEmailLogin}>
          <label className="block text-sm font-medium text-slate-700">
            Email
            <input
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none ring-indigo-500 transition focus:ring-2"
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              value={email}
            />
          </label>

          <label className="block text-sm font-medium text-slate-700">
            Password
            <input
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 outline-none ring-indigo-500 transition focus:ring-2"
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              value={password}
            />
          </label>

          {error ? <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p> : null}

          <button
            className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading}
            type="submit"
          >
            {loading ? 'Signing in...' : 'Login'}
          </button>
        </form>

        <button
          className="mt-3 w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          disabled={loading}
          onClick={handleGoogleLogin}
          type="button"
        >
          Continue with Google
        </button>

        <p className="mt-4 text-xs text-slate-500">
          Demo users: student@example.com, counsellor@example.com, mentor@example.com, admin@example.com.
        </p>
      </div>
    </div>
  )
}
