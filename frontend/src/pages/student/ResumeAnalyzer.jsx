import { FileUp } from 'lucide-react'
import { useMemo, useState } from 'react'
import PageShell from '../../components/common/PageShell'

const defaultResult = {
  score: 79,
  skills: ['React', 'Node.js', 'SQL', 'Problem Solving', 'Communication'],
  suggestions: [
    'Add quantifiable impact to project bullets.',
    'Highlight internship outcomes in first section.',
    'Use role-specific keywords from target job descriptions.',
  ],
}

export default function ResumeAnalyzer() {
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [fileName, setFileName] = useState('')
  const [result, setResult] = useState(null)

  const gaugeColor = useMemo(() => {
    if (!result) return 'bg-slate-300'
    if (result.score >= 80) return 'bg-emerald-500'
    if (result.score >= 65) return 'bg-amber-500'
    return 'bg-rose-500'
  }, [result])

  const analyze = (file) => {
    if (!file) return
    setFileName(file.name)
    setLoading(true)

    setTimeout(() => {
      setResult(defaultResult)
      setLoading(false)
    }, 1200)
  }

  return (
    <PageShell title="Resume Analyzer">
      <section className="rounded-2xl bg-white p-6 shadow">
        <h2 className="text-lg font-semibold text-slate-900">Upload resume (PDF)</h2>
        <label
          className={`mt-4 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 text-center transition ${
            dragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300 hover:bg-slate-50'
          }`}
          onDragEnter={() => setDragging(true)}
          onDragLeave={() => setDragging(false)}
          onDragOver={(event) => {
            event.preventDefault()
            setDragging(true)
          }}
          onDrop={(event) => {
            event.preventDefault()
            setDragging(false)
            analyze(event.dataTransfer.files?.[0])
          }}
        >
          <FileUp className="h-10 w-10 text-indigo-600" />
          <p className="mt-2 text-sm text-slate-700">Drag and drop your PDF here, or click to browse.</p>
          <input
            accept="application/pdf"
            className="hidden"
            onChange={(event) => analyze(event.target.files?.[0])}
            type="file"
          />
          {fileName ? <p className="mt-2 text-xs text-slate-500">Selected: {fileName}</p> : null}
        </label>
      </section>

      <section className="mt-6 rounded-2xl bg-white p-6 shadow">
        {loading ? (
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-600 border-r-transparent" />
            Analyzing your resume...
          </div>
        ) : result ? (
          <div className="space-y-6">
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Score Gauge</h3>
              <div className="mt-2 h-4 w-full overflow-hidden rounded-full bg-slate-100">
                <div className={`h-full ${gaugeColor}`} style={{ width: `${result.score}%` }} />
              </div>
              <p className="mt-2 text-sm font-semibold text-slate-900">{result.score} / 100</p>
            </div>

            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Extracted Skills</h3>
              <div className="mt-2 flex flex-wrap gap-2">
                {result.skills.map((skill) => (
                  <span className="rounded-full bg-indigo-100 px-3 py-1 text-xs font-medium text-indigo-700" key={skill}>
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Suggestions</h3>
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
                {result.suggestions.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-500">Upload a PDF resume to begin analysis.</p>
        )}
      </section>
    </PageShell>
  )
}
