import {
  Brain,
  Briefcase,
  FileText,
  GraduationCap,
  MessageSquare,
  Route,
  Sparkles,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import Chatbot from '../../components/student/Chatbot'
import PageShell from '../../components/common/PageShell'
import { useAuth } from '../../context/AuthContext'

const stats = [
  { label: 'Assessments done', value: '5 / 7' },
  { label: 'Resume score', value: '78 / 100' },
  { label: 'Placement %', value: '84%' },
]

const cards = [
  { title: 'Placement Predictor', description: 'Predict your chance and weak areas.', icon: Brain, to: '/student/placement-predictor' },
  { title: 'Resume Analyzer', description: 'Upload resume and get actionable feedback.', icon: FileText, to: '/student/resume-analyzer' },
  { title: 'Skill Gap', description: 'Compare your skills against target role.', icon: Sparkles, to: '/student/skill-gap' },
  { title: 'Learning Roadmap', description: 'Weekly roadmap with progress tracking.', icon: Route, to: '/student/learning-roadmap' },
  { title: 'Assessment Quiz', description: 'Evaluate your current level quickly.', icon: GraduationCap, to: '/student/assessment' },
  { title: 'Mentor Connect', description: 'Find mentors and schedule sessions.', icon: Briefcase, to: '/student/dashboard' },
  { title: 'Ask Assistant', description: 'Chat with smart career bot anytime.', icon: MessageSquare, to: '/student/dashboard' },
]

export default function StudentDashboard() {
  const auth = useAuth()

  return (
    <PageShell title="Student Dashboard">
      <section className="rounded-2xl bg-gradient-to-r from-indigo-600 to-cyan-500 p-6 text-white shadow-lg">
        <p className="text-sm uppercase tracking-widest text-indigo-100">Welcome back</p>
        <h2 className="mt-1 text-2xl font-semibold">{auth.full_name || 'Student'}</h2>
        <p className="mt-1 text-sm text-indigo-100">Track your progress and take the next best career action.</p>
      </section>

      <section className="mt-6 grid gap-4 md:grid-cols-3">
        {stats.map((item) => (
          <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm" key={item.label}>
            <p className="text-sm text-slate-500">{item.label}</p>
            <p className="mt-1 text-2xl font-semibold text-slate-900">{item.value}</p>
          </article>
        ))}
      </section>

      <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {cards.map((item) => (
          <Link
            className="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            key={item.title}
            to={item.to}
          >
            <item.icon className="h-7 w-7 text-indigo-600" />
            <h3 className="mt-3 text-lg font-semibold text-slate-900 group-hover:text-indigo-600">{item.title}</h3>
            <p className="mt-1 text-sm text-slate-600">{item.description}</p>
          </Link>
        ))}
      </section>

      <Chatbot />
    </PageShell>
  )
}
