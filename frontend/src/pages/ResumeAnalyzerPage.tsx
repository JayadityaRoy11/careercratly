import { useState } from 'react'
import { toast } from 'sonner'
import { AnalysisDashboard } from '@/components/resume/AnalysisDashboard'
import { UploadDropzone } from '@/components/resume/UploadDropzone'
import { ErrorState, LoadingState } from '@/components/common/ErrorState'
import { PageShell } from '@/components/layout/PageShell'
import { Button } from '@/components/ui/button'
import { TARGET_ROLES } from '@/data/roles'
import { analyzeResume, getCourseRecommendations, getProjectResources, uploadResume } from '@/services/resume'
import { parseApiError } from '@/lib/api'
import { useSessionStore } from '@/store/session'
import type { CourseRecommendResponse, ProjectResourcesResponse } from '@/types'

export function ResumeAnalyzerPage() {
  const { resume, analysis, targetRole, setResume, setAnalysis, setTargetRole } = useSessionStore()
  const [file, setFile] = useState<File | null>(null)
  const [customRole, setCustomRole] = useState('')
  const [status, setStatus] = useState('')
  const [busy, setBusy] = useState<'upload' | 'analyze' | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [courses, setCourses] = useState<CourseRecommendResponse | null>(null)
  const [projects, setProjects] = useState<ProjectResourcesResponse | null>(null)

  const role = customRole.trim() || targetRole

  const handleAnalyze = async () => {
    setError(null)
    setCourses(null)
    setProjects(null)
    try {
      let current = resume
      if (file) {
        setBusy('upload')
        setStatus('Extracting your experience...')
        current = await uploadResume(file, () => undefined)
        setResume(current)
        toast.success('Resume parsed')
      }
      if (!current) {
        setError('Upload a PDF or DOCX resume first.')
        return
      }
      setBusy('analyze')
      setStatus('Mapping your skills...')
      const result = await analyzeResume(current.resume_id, role)
      setAnalysis(result)
      setTargetRole(role)
      const [courseData, projectData] = await Promise.all([
        getCourseRecommendations({ resumeId: current.resume_id, targetRole: role }),
        getProjectResources(result.recommended_project_themes[0] || role),
      ])
      setCourses(courseData)
      setProjects(projectData)
    } catch (err) {
      setError(parseApiError(err).message)
    } finally {
      setBusy(null)
      setStatus('')
    }
  }

  return (
    <PageShell>
      <p className="text-xs uppercase tracking-[0.28em] text-primary">Resume Intelligence</p>
      <h1 className="font-display text-3xl sm:text-5xl mt-3">Understand how your resume aligns with your target role.</h1>

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        <UploadDropzone
          file={file}
          onFile={setFile}
          status={resume && !file ? `Last upload: ${resume.filename}` : status}
        />
        <div className="glass rounded-3xl p-6 space-y-4">
          <label className="text-sm" htmlFor="role">
            Target role
          </label>
          <select
            id="role"
            className="w-full rounded-xl bg-bg border border-border px-3 py-2"
            value={(TARGET_ROLES as readonly string[]).includes(targetRole) ? targetRole : 'Backend Developer'}
            onChange={(e) => {
              setTargetRole(e.target.value)
              setCustomRole('')
            }}
          >
            {TARGET_ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
          <input
            className="w-full rounded-xl bg-bg border border-border px-3 py-2"
            placeholder="Or type a custom role"
            value={customRole}
            onChange={(e) => setCustomRole(e.target.value)}
            aria-label="Custom target role"
          />
          <Button className="w-full" onClick={() => void handleAnalyze()} disabled={!!busy}>
            Analyze Resume
          </Button>
        </div>
      </div>

      {busy ? <LoadingState className="mt-8" title={status || 'Working...'} detail="This stays on your session — no login." /> : null}
      {error ? <div className="mt-8"><ErrorState message={error} onRetry={() => void handleAnalyze()} /></div> : null}

      {analysis ? <AnalysisDashboard analysis={analysis} courses={courses} projects={projects} /> : null}
    </PageShell>
  )
}
