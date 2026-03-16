import { useMemo, useState } from 'react'
import PageShell from '../../components/common/PageShell'

const seedUsers = [
  { id: 1, name: 'Aisha Khan', email: 'aisha@example.com', role: 'student', active: true },
  { id: 2, name: 'Rahul Mehta', email: 'rahul@example.com', role: 'mentor', active: true },
  { id: 3, name: 'Nina Roy', email: 'nina@example.com', role: 'counsellor', active: false },
  { id: 4, name: 'Mina Das', email: 'mina@example.com', role: 'student', active: true },
]

export default function UserManagement() {
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [users, setUsers] = useState(seedUsers)

  const filtered = useMemo(() => {
    return users.filter((user) => {
      const query = search.toLowerCase()
      const matchesQuery =
        user.name.toLowerCase().includes(query) || user.email.toLowerCase().includes(query)
      const matchesRole = roleFilter === 'all' || user.role === roleFilter
      return matchesQuery && matchesRole
    })
  }, [users, search, roleFilter])

  const exportCsv = () => {
    const header = ['id', 'name', 'email', 'role', 'active']
    const rows = filtered.map((user) => [user.id, user.name, user.email, user.role, user.active])
    const csvContent = [header, ...rows].map((row) => row.join(',')).join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'users.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <PageShell
      actions={
        <button
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500"
          onClick={exportCsv}
          type="button"
        >
          Export CSV
        </button>
      }
      title="User Management"
    >
      <section className="rounded-2xl bg-white p-6 shadow">
        <div className="mb-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm md:max-w-sm"
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search by name or email"
            value={search}
          />
          <select
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
            onChange={(event) => setRoleFilter(event.target.value)}
            value={roleFilter}
          >
            <option value="all">All roles</option>
            <option value="student">Student</option>
            <option value="counsellor">Counsellor</option>
            <option value="mentor">Mentor</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500">
                <th className="py-2 pr-3">Name</th>
                <th className="py-2 pr-3">Email</th>
                <th className="py-2 pr-3">Role</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((user) => (
                <tr className="border-b border-slate-100" key={user.id}>
                  <td className="py-3 pr-3 font-medium text-slate-900">{user.name}</td>
                  <td className="py-3 pr-3 text-slate-600">{user.email}</td>
                  <td className="py-3 pr-3">
                    <select
                      className="rounded border border-slate-300 px-2 py-1"
                      onChange={(event) => {
                        const role = event.target.value
                        setUsers((prev) => prev.map((item) => (item.id === user.id ? { ...item, role } : item)))
                      }}
                      value={user.role}
                    >
                      <option value="student">Student</option>
                      <option value="counsellor">Counsellor</option>
                      <option value="mentor">Mentor</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                  <td className="py-3">
                    <label className="inline-flex items-center gap-2 text-slate-700">
                      <input
                        checked={user.active}
                        onChange={(event) => {
                          const active = event.target.checked
                          setUsers((prev) => prev.map((item) => (item.id === user.id ? { ...item, active } : item)))
                        }}
                        type="checkbox"
                      />
                      {user.active ? 'Active' : 'Inactive'}
                    </label>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </PageShell>
  )
}
