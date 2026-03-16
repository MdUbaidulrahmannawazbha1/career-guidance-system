import { useMemo, useState } from 'react'
import PageShell from '../../components/common/PageShell'

const clamp = (value, min, max) => Math.min(max, Math.max(min, value))

const calculatePlacement = ({ cgpa, skills, projects, internship, backlogs }) => {
  const score = cgpa * 7 + skills * 3 + projects * 4 + (internship ? 10 : 0) - backlogs * 6
  return clamp(Math.round(score), 0, 100)
}

export default function PlacementPredictor() {
  const [form, setForm] = useState({ cgpa: 7.5, skills: 6, projects: 2, internship: true, backlogs: 0 })
  const [simulator, setSimulator] = useState({ cgpa: 8, skills: 8, projects: 3, internship: true, backlogs: 0 })

  const percentage = useMemo(() => calculatePlacement(form), [form])
  const simulatedPercentage = useMemo(() => calculatePlacement(simulator), [simulator])

  const weakAreas = useMemo(() => {
    const issues = []
    if (form.cgpa < 7) issues.push('CGPA below 7.0')
    if (form.skills < 6) issues.push('Limited core skills')
    if (form.projects < 2) issues.push('Not enough projects')
    if (!form.internship) issues.push('No internship experience')
    if (form.backlogs > 0) issues.push('Existing backlogs')
    return issues
  }, [form])

  return (
    <PageShell title="Placement Predictor">
      <div className="grid gap-6 xl:grid-cols-2">
        <section className="rounded-2xl bg-white p-6 shadow">
          <h2 className="text-lg font-semibold text-slate-900">Current profile</h2>
          <div className="mt-4 space-y-4">
            <label className="block text-sm font-medium text-slate-700">
              CGPA: <span className="font-semibold">{form.cgpa.toFixed(1)}</span>
              <input
                className="mt-2 w-full"
                max="10"
                min="0"
                onChange={(event) => setForm((prev) => ({ ...prev, cgpa: Number(event.target.value) }))}
                step="0.1"
                type="range"
                value={form.cgpa}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Skills count: <span className="font-semibold">{form.skills}</span>
              <input
                className="mt-2 w-full"
                max="20"
                min="0"
                onChange={(event) => setForm((prev) => ({ ...prev, skills: Number(event.target.value) }))}
                type="range"
                value={form.skills}
              />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Projects
              <input
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                min="0"
                onChange={(event) => setForm((prev) => ({ ...prev, projects: Number(event.target.value) }))}
                type="number"
                value={form.projects}
              />
            </label>
            <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <input
                checked={form.internship}
                onChange={(event) => setForm((prev) => ({ ...prev, internship: event.target.checked }))}
                type="checkbox"
              />
              Internship experience
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Backlogs
              <input
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                min="0"
                onChange={(event) => setForm((prev) => ({ ...prev, backlogs: Number(event.target.value) }))}
                type="number"
                value={form.backlogs}
              />
            </label>
          </div>
        </section>

        <section className="rounded-2xl bg-white p-6 shadow">
          <h2 className="text-lg font-semibold text-slate-900">Prediction</h2>
          <div className="mx-auto mt-4 flex h-44 w-44 items-center justify-center rounded-full border-[14px] border-indigo-100">
            <div
              className="absolute h-44 w-44 rounded-full border-[14px] border-transparent border-t-indigo-600 transition-transform duration-700"
              style={{ transform: `rotate(${(percentage / 100) * 360}deg)` }}
            />
            <div className="relative rounded-full bg-white px-4 py-2 text-center">
              <p className="text-3xl font-bold text-slate-900">{percentage}%</p>
              <p className="text-xs text-slate-500">Placement chance</p>
            </div>
          </div>

          <h3 className="mt-6 text-sm font-semibold uppercase tracking-wide text-slate-500">Weak areas</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {weakAreas.length ? (
              weakAreas.map((item) => (
                <span className="rounded-full bg-rose-100 px-3 py-1 text-xs font-medium text-rose-700" key={item}>
                  {item}
                </span>
              ))
            ) : (
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">No major weak areas</span>
            )}
          </div>
        </section>
      </div>

      <section className="mt-6 rounded-2xl bg-white p-6 shadow">
        <h2 className="text-lg font-semibold text-slate-900">What-if simulator</h2>
        <p className="text-sm text-slate-600">Adjust values to see live impact.</p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <label className="text-sm font-medium text-slate-700">
            CGPA: {simulator.cgpa.toFixed(1)}
            <input
              className="mt-1 w-full"
              max="10"
              min="0"
              onChange={(event) => setSimulator((prev) => ({ ...prev, cgpa: Number(event.target.value) }))}
              step="0.1"
              type="range"
              value={simulator.cgpa}
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Skills: {simulator.skills}
            <input
              className="mt-1 w-full"
              max="20"
              min="0"
              onChange={(event) => setSimulator((prev) => ({ ...prev, skills: Number(event.target.value) }))}
              type="range"
              value={simulator.skills}
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Projects: {simulator.projects}
            <input
              className="mt-1 w-full"
              max="10"
              min="0"
              onChange={(event) => setSimulator((prev) => ({ ...prev, projects: Number(event.target.value) }))}
              type="range"
              value={simulator.projects}
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Backlogs: {simulator.backlogs}
            <input
              className="mt-1 w-full"
              max="10"
              min="0"
              onChange={(event) => setSimulator((prev) => ({ ...prev, backlogs: Number(event.target.value) }))}
              type="range"
              value={simulator.backlogs}
            />
          </label>
        </div>
        <p className="mt-4 text-sm text-slate-700">
          Simulated placement chance: <span className="font-semibold text-indigo-700">{simulatedPercentage}%</span>
        </p>
      </section>
    </PageShell>
  )
}
