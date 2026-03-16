import {
  Bar,
  BarChart,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import PageShell from '../../components/common/PageShell'

const stats = [
  { label: 'Total users', value: 1240 },
  { label: 'Assessments', value: 892 },
  { label: 'Predictions', value: 731 },
  { label: 'Mentors', value: 52 },
]

const usersByRole = [
  { name: 'Students', value: 900, color: '#4f46e5' },
  { name: 'Counsellors', value: 120, color: '#0ea5e9' },
  { name: 'Mentors', value: 180, color: '#14b8a6' },
  { name: 'Admins', value: 40, color: '#f59e0b' },
]

const assessmentsOverTime = [
  { month: 'Jan', count: 80 },
  { month: 'Feb', count: 120 },
  { month: 'Mar', count: 160 },
  { month: 'Apr', count: 140 },
  { month: 'May', count: 190 },
]

const topCareers = [
  { career: 'Software Engineer', count: 220 },
  { career: 'Data Analyst', count: 180 },
  { career: 'Product Manager', count: 120 },
  { career: 'UI/UX Designer', count: 95 },
  { career: 'DevOps Engineer', count: 88 },
]

export default function AdminDashboard() {
  return (
    <PageShell title="Admin Dashboard">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((item) => (
          <article className="rounded-2xl bg-white p-5 shadow" key={item.label}>
            <p className="text-sm text-slate-500">{item.label}</p>
            <p className="mt-2 text-3xl font-semibold text-slate-900">{item.value}</p>
          </article>
        ))}
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <article className="rounded-2xl bg-white p-5 shadow">
          <h2 className="text-lg font-semibold text-slate-900">Users by role</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={usersByRole} dataKey="value" innerRadius={70} outerRadius={100} paddingAngle={3}>
                  {usersByRole.map((entry) => (
                    <Cell fill={entry.color} key={entry.name} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="rounded-2xl bg-white p-5 shadow">
          <h2 className="text-lg font-semibold text-slate-900">Assessments over time</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer>
              <LineChart data={assessmentsOverTime}>
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line dataKey="count" stroke="#4f46e5" strokeWidth={3} type="monotone" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <section className="mt-6 rounded-2xl bg-white p-5 shadow">
        <h2 className="text-lg font-semibold text-slate-900">Top 5 predicted careers</h2>
        <div className="mt-4 h-72">
          <ResponsiveContainer>
            <BarChart data={topCareers}>
              <XAxis dataKey="career" interval={0} tick={{ fontSize: 11 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </PageShell>
  )
}
