import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './components/common/ProtectedRoute'
import { roleDashboardPath, useAuth } from './context/AuthContext'
import Login from './pages/auth/Login'
import AdminDashboard from './pages/admin/Dashboard'
import UserManagement from './pages/admin/UserManagement'
import CounsellorDashboard from './pages/counsellor/Dashboard'
import MentorDashboard from './pages/mentor/Dashboard'
import AssessmentPage from './pages/student/AssessmentPage'
import LearningRoadmap from './pages/student/LearningRoadmap'
import PlacementPredictor from './pages/student/PlacementPredictor'
import ResumeAnalyzer from './pages/student/ResumeAnalyzer'
import SkillGap from './pages/student/SkillGap'
import StudentDashboard from './pages/student/Dashboard'

function RootRedirect() {
  const auth = useAuth()

  if (!auth.isAuthenticated()) {
    return <Navigate replace to="/login" />
  }

  return <Navigate replace to={roleDashboardPath[auth.role] || '/login'} />
}

function NotFound() {
  return <Navigate replace to="/" />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<RootRedirect />} path="/" />
        <Route element={<Login />} path="/login" />

        <Route element={<ProtectedRoute allowedRoles={['student']} />}>
          <Route element={<StudentDashboard />} path="/student/dashboard" />
          <Route element={<PlacementPredictor />} path="/student/placement-predictor" />
          <Route element={<ResumeAnalyzer />} path="/student/resume-analyzer" />
          <Route element={<SkillGap />} path="/student/skill-gap" />
          <Route element={<LearningRoadmap />} path="/student/learning-roadmap" />
          <Route element={<AssessmentPage />} path="/student/assessment" />
        </Route>

        <Route element={<ProtectedRoute allowedRoles={['counsellor']} />}>
          <Route element={<CounsellorDashboard />} path="/counsellor/dashboard" />
        </Route>

        <Route element={<ProtectedRoute allowedRoles={['mentor']} />}>
          <Route element={<MentorDashboard />} path="/mentor/dashboard" />
        </Route>

        <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
          <Route element={<AdminDashboard />} path="/admin/dashboard" />
          <Route element={<UserManagement />} path="/admin/users" />
        </Route>

        <Route element={<NotFound />} path="*" />
      </Routes>
    </BrowserRouter>
  )
}
