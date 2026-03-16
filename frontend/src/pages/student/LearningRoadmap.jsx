import { useMemo, useState } from 'react'
import PageShell from '../../components/common/PageShell'

const initialWeeks = [
  {
    week: 'Week 1',
    topic: 'Core JavaScript and Problem Solving',
    resources: ['JavaScript.info fundamentals', 'LeetCode easy set'],
    project: 'Build a calculator app',
    done: true,
  },
  {
    week: 'Week 2',
    topic: 'React Basics and Component Design',
    resources: ['React docs quick start', 'State management basics'],
    project: 'Build a task manager app',
    done: false,
  },
  {
    week: 'Week 3',
    topic: 'Backend APIs and SQL',
    resources: ['REST API fundamentals', 'SQLBolt practice'],
    project: 'Create a student profile API',
    done: false,
  },
]

export default function LearningRoadmap() {
  const [weeks, setWeeks] = useState(initialWeeks)

  const progress = useMemo(() => {
    const completed = weeks.filter((item) => item.done).length
    return Math.round((completed / weeks.length) * 100)
  }, [weeks])

  return (
    <PageShell title="Learning Roadmap">
      <section className="rounded-2xl bg-white p-6 shadow">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Progress</h2>
          <span className="text-sm font-semibold text-indigo-700">{progress}% complete</span>
        </div>
        <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-slate-100">
          <div className="h-full rounded-full bg-indigo-600 transition-all" style={{ width: `${progress}%` }} />
        </div>
      </section>

      <section className="mt-6 space-y-4">
        {weeks.map((item, index) => (
          <article className="relative rounded-2xl border border-slate-200 bg-white p-5 shadow-sm" key={item.week}>
            {index < weeks.length - 1 ? <span className="absolute -bottom-5 left-6 h-5 w-0.5 bg-slate-300" /> : null}
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600">{item.week}</p>
                <h3 className="mt-1 text-lg font-semibold text-slate-900">{item.topic}</h3>
                <p className="mt-2 text-sm text-slate-600">Resources: {item.resources.join(' • ')}</p>
                <p className="mt-1 text-sm text-slate-600">Mini project: {item.project}</p>
              </div>
              <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                <input
                  checked={item.done}
                  onChange={(event) => {
                    const checked = event.target.checked
                    setWeeks((prev) => prev.map((week) => (week.week === item.week ? { ...week, done: checked } : week)))
                  }}
                  type="checkbox"
                />
                Complete
              </label>
            </div>
          </article>
        ))}
      </section>
    </PageShell>
  )
}
