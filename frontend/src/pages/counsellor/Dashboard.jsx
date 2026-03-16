import PageShell from '../../components/common/PageShell'

export default function CounsellorDashboard() {
  return (
    <PageShell title="Counsellor Dashboard">
      <section className="rounded-2xl bg-white p-6 shadow">
        <h2 className="text-lg font-semibold text-slate-900">Counsellor workspace</h2>
        <p className="mt-2 text-sm text-slate-600">Review student progress, run counselling sessions, and assign roadmaps.</p>
      </section>
    </PageShell>
  )
}
