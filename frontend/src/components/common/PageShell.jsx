import { LogOut } from 'lucide-react'
import { Link } from 'react-router-dom'
import { roleDashboardPath } from '../../context/authConfig'
import { useAuth } from '../../context/useAuth'

export default function PageShell({ title, children, actions }) {
  const auth = useAuth()
  const homePath = roleDashboardPath[auth.role] ?? '/login'

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <Link className="text-sm font-semibold uppercase tracking-widest text-indigo-600" to={homePath}>
              Career Compass
            </Link>
            <h1 className="mt-1 text-xl font-semibold">{title}</h1>
          </div>
          <div className="flex items-center gap-3">
            {actions}
            <button
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-100"
              onClick={auth.logout}
              type="button"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  )
}
