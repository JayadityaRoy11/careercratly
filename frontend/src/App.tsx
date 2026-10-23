import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import { Cursor } from '@/components/common/Cursor'
import { Layout } from '@/components/layout/Layout'

const LandingPage = lazy(() => import('@/pages/LandingPage').then((m) => ({ default: m.LandingPage })))
const ResumeAnalyzerPage = lazy(() =>
  import('@/pages/ResumeAnalyzerPage').then((m) => ({ default: m.ResumeAnalyzerPage })),
)
const JobPortalPage = lazy(() => import('@/pages/JobPortalPage').then((m) => ({ default: m.JobPortalPage })))
const InterviewPrepPage = lazy(() =>
  import('@/pages/InterviewPrepPage').then((m) => ({ default: m.InterviewPrepPage })),
)
const AboutPage = lazy(() => import('@/pages/AboutPage').then((m) => ({ default: m.AboutPage })))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage').then((m) => ({ default: m.NotFoundPage })))

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Cursor />
        <Toaster theme="dark" position="top-right" />
        <Suspense fallback={<div className="min-h-screen grid place-items-center text-muted">Loading workspace…</div>}>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/" element={<LandingPage />} />
              <Route path="/resume-analyzer" element={<ResumeAnalyzerPage />} />
              <Route path="/job-portal" element={<JobPortalPage />} />
              <Route path="/interview-prep" element={<InterviewPrepPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/login" element={<Navigate to="/" replace />} />
              <Route path="/register" element={<Navigate to="/" replace />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  )
}
