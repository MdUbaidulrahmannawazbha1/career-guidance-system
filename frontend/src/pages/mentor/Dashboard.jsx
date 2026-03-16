import PageShell from '../../components/common/PageShell'

export default function MentorDashboard() {
  return (
    <PageShell title="Mentor Dashboard">
      <section className="rounded-2xl bg-white p-6 shadow">
        <h2 className="text-lg font-semibold text-slate-900">Mentor workspace</h2>
        <p className="mt-2 text-sm text-slate-600">Track mentee goals, share feedback, and schedule mentoring activities.</p>
      </section>
    </PageShell>
  )
}
