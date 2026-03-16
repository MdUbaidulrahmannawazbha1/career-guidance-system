import { useMemo, useState } from 'react'

const questions = [
  { id: 1, text: 'How comfortable are you with Data Structures?', answer: 1 },
  { id: 2, text: 'Can you build a CRUD app independently?', answer: 2 },
  { id: 3, text: 'How often do you participate in coding challenges?', answer: 2 },
]

const options = ['Beginner', 'Intermediate', 'Advanced']

const getLevel = (score) => {
  if (score <= 1) return 'Beginner'
  if (score <= 4) return 'Intermediate'
  return 'Advanced'
}

export default function AssessmentQuiz() {
  const [current, setCurrent] = useState(0)
  const [score, setScore] = useState(0)
  const [feedback, setFeedback] = useState(null)
  const [done, setDone] = useState(false)

  const progress = useMemo(() => ((current + (done ? 1 : 0)) / questions.length) * 100, [current, done])

  const submitAnswer = (index) => {
    const isCorrect = index === questions[current].answer
    setFeedback(isCorrect ? 'correct' : 'wrong')
    if (isCorrect) {
      setScore((prev) => prev + 2)
    }

    setTimeout(() => {
      setFeedback(null)
      if (current + 1 === questions.length) {
        setDone(true)
      } else {
        setCurrent((prev) => prev + 1)
      }
    }, 350)
  }

  if (done) {
    const level = getLevel(score)
    return (
      <div className="rounded-2xl bg-white p-6 shadow">
        <h3 className="text-xl font-semibold text-slate-900">Assessment Complete</h3>
        <p className="mt-2 text-slate-600">Final score: {score} / 6</p>
        <span className="mt-4 inline-block rounded-full bg-indigo-100 px-4 py-1 text-sm font-semibold text-indigo-700">
          {level}
        </span>
      </div>
    )
  }

  return (
    <div className="rounded-2xl bg-white p-6 shadow">
      <div className="mb-4 h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-indigo-600 transition-all" style={{ width: `${progress}%` }} />
      </div>
      <p className="text-sm text-slate-500">
        Question {current + 1} of {questions.length}
      </p>
      <h3 className="mt-1 text-lg font-semibold text-slate-900">{questions[current].text}</h3>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        {options.map((option, index) => (
          <button
            className={`rounded-lg border px-3 py-2 text-sm font-medium transition ${
              feedback === null
                ? 'border-slate-300 hover:bg-slate-50'
                : feedback === 'correct'
                  ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
                  : 'border-rose-200 bg-rose-50 text-rose-700'
            }`}
            key={option}
            onClick={() => submitAnswer(index)}
            type="button"
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  )
}
