import { useMemo, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from 'recharts'
import PageShell from '../../components/common/PageShell'

const skillMap = {
  'Frontend Developer': [
    { skill: 'HTML/CSS', have: 1 },
    { skill: 'React', have: 1 },
    { skill: 'TypeScript', have: 0 },
    { skill: 'Testing', have: 0 },
  ],
  'Data Analyst': [
    { skill: 'SQL', have: 1 },
    { skill: 'Python', have: 1 },
    { skill: 'Power BI', have: 0 },
    { skill: 'Statistics', have: 0 },
  ],
}

const resources = {
  TypeScript: ['TypeScript Handbook', 'TS in 100 Days roadmap'],
  Testing: ['Jest + RTL crash course', 'Frontend testing patterns'],
  'Power BI': ['Power BI guided learning', 'DAX fundamentals'],
  Statistics: ['Khan Academy Statistics', 'Practical Stats for DS'],
}

export default function SkillGap() {
  const [career, setCareer] = useState('Frontend Developer')
  const [selectedSkill, setSelectedSkill] = useState('')

  const data = useMemo(
    () => (skillMap[career] || []).map((item) => ({ ...item, value: item.have ? 100 : 0 })),
    [career],
  )

  return (
    <PageShell title="Skill Gap Analysis">
      <section className="rounded-2xl bg-white p-6 shadow">
        <label className="text-sm font-medium text-slate-700">
          Target career
          <select
            className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 md:w-96"
            onChange={(event) => setCareer(event.target.value)}
            value={career}
          >
            {Object.keys(skillMap).map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <div className="mt-6 h-80">
          <ResponsiveContainer>
            <BarChart data={data} layout="vertical" margin={{ left: 24, right: 24 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis hide type="number" />
              <YAxis dataKey="skill" type="category" width={120} />
              <Bar dataKey="value" radius={[8, 8, 8, 8]}>
                <LabelList dataKey="have" formatter={(value) => (value ? 'Have' : 'Missing')} position="right" />
                {data.map((entry) => (
                  <Bar dataKey="value" fill={entry.have ? '#16a34a' : '#dc2626'} key={entry.skill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {data
            .filter((item) => !item.have)
            .map((item) => (
              <button
                className="rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-xs font-semibold text-rose-700"
                key={item.skill}
                onClick={() => setSelectedSkill(item.skill)}
                type="button"
              >
                {item.skill}
              </button>
            ))}
        </div>
      </section>

      {selectedSkill ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4">
          <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold text-slate-900">Resources for {selectedSkill}</h3>
            <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">
              {(resources[selectedSkill] || ['Curated learning links coming soon']).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <button
              className="mt-5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white"
              onClick={() => setSelectedSkill('')}
              type="button"
            >
              Close
            </button>
          </div>
        </div>
      ) : null}
    </PageShell>
  )
}
