import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { EmptyState, ErrorState, LoadingState } from '@/components/common/ErrorState'
import { PageShell } from '@/components/layout/PageShell'
import { EMPLOYMENT_TYPES, FIELD_FILTERS, LOCATIONS, WORK_MODES } from '@/data/roles'
import { parseApiError } from '@/lib/api'
import { getJobSources, matchJobsToResume, searchJobs } from '@/services/jobs'
import { useSessionStore } from '@/store/session'
import type { JobListing, MatchedJob, ProviderStatus } from '@/types'

export function JobPortalPage() {
  const resume = useSessionStore((s) => s.resume)
  const [role, setRole] = useState('')
  const [location, setLocation] = useState('')
  const [workMode, setWorkMode] = useState('')
  const [employment, setEmployment] = useState('')
  const [experience, setExperience] = useState('')
  const [source, setSource] = useState('all')
  const [items, setItems] = useState<(JobListing | MatchedJob)[]>([])
  const [sources, setSources] = useState<ProviderStatus[]>([])
  const [matched, setMatched] = useState(false)
  const [phase, setPhase] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const filters = useMemo(
    () => ({
      role: role || undefined,
      location: location || undefined,
      work_mode: workMode || undefined,
      employment_type: employment || undefined,
      experience_level: experience || undefined,
      source: source === 'all' ? undefined : source,
    }),
    [role, location, workMode, employment, experience, source],
  )

  const load = async () => {
    setBusy(true)
    setError(null)
    setMatched(false)
    setPhase('Searching across connected sources...')
    try {
      const [data, status] = await Promise.all([searchJobs(filters), getJobSources()])
      setItems(data.items)
      setSources(status.sources)
    } catch (err) {
      setError(parseApiError(err).message)
    } finally {
      setBusy(false)
      setPhase('')
    }
  }

  useEffect(() => {
    let ignore = false
    const boot = async () => {
      setBusy(true)
      setPhase('Searching across connected sources...')
      try {
        const [data, status] = await Promise.all([searchJobs({}), getJobSources()])
        if (ignore) return
        setItems(data.items)
        setSources(status.sources)
      } catch (err) {
        if (!ignore) setError(parseApiError(err).message)
      } finally {
        if (!ignore) {
          setBusy(false)
          setPhase('')
        }
      }
    }
    void boot()
    return () => {
      ignore = true
    }
  }, [])

  const onMatch = async () => {
    if (!resume) return
    setBusy(true)
    setError(null)
    setPhase('Matching opportunities to your profile...')
    try {
      const data = await matchJobsToResume(resume.resume_id, filters)
      setItems(data.items)
      setMatched(true)
      if (data.sources) setSources(data.sources)
    } catch (err) {
      setError(parseApiError(err).message)
    } finally {
      setBusy(false)
      setPhase('')
    }
  }

  const selectedUnavailable =
    source !== 'all' &&
    source !== 'mock' &&
    sources.find((row) => row.provider === source)?.status === 'not_configured'

  return (
    <PageShell>
      <p className="text-xs uppercase tracking-[0.28em] text-primary">Job portal</p>
      <h1 className="font-display text-3xl sm:text-6xl mt-3">FIND THE ROLE THAT FITS YOU.</h1>
      <p className="text-muted mt-3 max-w-2xl">
        Live sources require authorized APIs. Demo listings are labeled and are not vacancies.
        Resume Match is not a company ATS rank.
      </p>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {sources.map((row) => (
          <div key={row.provider} className="glass rounded-2xl p-4 text-sm">
            <p className="font-display">
              {row.provider === 'mock' ? 'Demo Jobs' : row.provider === 'linkedin' ? 'LinkedIn' : row.provider === 'naukri' ? 'Naukri' : row.provider}
            </p>
            <p className={row.live ? 'text-success' : row.status === 'demo' ? 'text-warning' : 'text-muted'}>
              {row.live ? 'Connected' : row.status === 'demo' ? 'Demo' : 'Not configured'}
            </p>
            <p className="text-xs text-muted mt-1">{row.message}</p>
          </div>
        ))}
      </div>

      <fieldset className="mt-6">
        <legend className="text-sm text-muted mb-2">Job sources</legend>
        <div className="flex flex-wrap gap-2">
          {[
            ['all', 'All Sources'],
            ['linkedin', 'LinkedIn'],
            ['naukri', 'Naukri'],
            ['mock', 'Demo Jobs'],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => setSource(value)}
              className={`rounded-full px-4 py-2 text-sm min-h-11 cursor-pointer ${
                source === value ? 'bg-primary text-bg' : 'bg-white/5'
              }`}
            >
              {label}
              {value !== 'all' && value !== 'mock' && sources.find((s) => s.provider === value)?.status === 'not_configured'
                ? ' · unavailable'
                : ''}
            </button>
          ))}
        </div>
      </fieldset>

      <div className="mt-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
        <Select label="Field / role" value={role} onChange={setRole} options={['', ...FIELD_FILTERS]} />
        <Select label="Location" value={location} onChange={setLocation} options={['', ...LOCATIONS]} />
        <Select
          label="Work mode"
          value={workMode}
          onChange={setWorkMode}
          options={['', ...WORK_MODES.map((w) => w.value)]}
          labels={{ '': 'Any', remote: 'Remote', hybrid: 'Hybrid', onsite: 'On-site' }}
        />
        <Select
          label="Employment"
          value={employment}
          onChange={setEmployment}
          options={['', ...EMPLOYMENT_TYPES.map((e) => e.value)]}
          labels={{ '': 'Any', internship: 'Internship', full_time: 'Full-time', part_time: 'Part-time' }}
        />
        <Select
          label="Experience"
          value={experience}
          onChange={setExperience}
          options={['', 'internship', 'entry', 'mid']}
          labels={{ '': 'Any', internship: 'Internship', entry: 'Entry', mid: 'Mid' }}
        />
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <Button onClick={() => void load()} disabled={busy}>
          Apply filters
        </Button>
        <Button variant="secondary" onClick={() => void onMatch()} disabled={busy || !resume}>
          Match jobs to my resume
        </Button>
        {!resume ? (
          <Link to="/resume-analyzer" className="text-sm text-primary self-center min-h-11 inline-flex items-center">
            Upload a resume first
          </Link>
        ) : null}
      </div>

      {busy ? (
        <div className="mt-8 space-y-4">
          <LoadingState title={phase || 'Searching...'} />
          {[0, 1, 2].map((i) => (
            <div key={i} className="glass rounded-2xl p-5 animate-pulse">
              <div className="h-5 w-1/3 rounded bg-white/10" />
              <div className="h-3 w-2/3 rounded bg-white/10 mt-3" />
              <div className="h-16 rounded bg-white/5 mt-4" />
            </div>
          ))}
        </div>
      ) : null}
      {error ? (
        <div className="mt-8">
          <ErrorState message={error} onRetry={() => void load()} />
        </div>
      ) : null}
      {selectedUnavailable ? (
        <p className="mt-6 text-sm text-muted">
          {source === 'linkedin'
            ? 'LinkedIn integration is not configured for this environment.'
            : 'Naukri integration is not configured for this environment.'}{' '}
          Demo listings remain available under Demo Jobs.
        </p>
      ) : null}
      {!busy && !error && items.length === 0 ? (
        <div className="mt-8">
          <EmptyState title="No listings" message="Try All Sources or Demo Jobs." />
        </div>
      ) : null}

      <div className="mt-8 grid gap-4">
        {items.map((job) => (
          <article key={job.id} className="glass rounded-2xl p-5">
            <div className="flex flex-wrap justify-between gap-3">
              <div className="min-w-0">
                <h2 className="font-display text-xl">{job.title}</h2>
                <p className="text-sm text-muted break-words">
                  {job.company} · {job.location} · {job.work_mode} · {job.employment_type.replace('_', ' ')}
                </p>
                <p className="text-xs mt-1 text-warning">{job.is_demo || job.source === 'mock' ? 'Demo listing' : job.source}</p>
              </div>
              {'match_score' in job ? (
                <p className="text-primary font-display text-2xl">{job.match_score}% Resume Match</p>
              ) : null}
            </div>
            <p className="text-sm mt-3 text-muted">{job.description}</p>
            <p className="text-xs text-muted mt-2">Posted {job.posted_date || 'n/a'}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {job.skills.map((s) => (
                <span key={s} className="text-xs border border-border rounded-full px-2 py-1">
                  {s}
                </span>
              ))}
            </div>
            {matched && 'matched_skills' in job ? (
              <p className="text-xs mt-3 text-success">Matched: {job.matched_skills.join(', ') || '—'}</p>
            ) : null}
            {matched && 'missing_skills' in job ? (
              <p className="text-xs text-danger">Missing: {job.missing_skills.join(', ') || '—'}</p>
            ) : null}
            <a
              className="inline-flex items-center gap-1 mt-4 text-sm text-primary min-h-11"
              href={job.external_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              View Job <ExternalLink className="size-3.5" />
            </a>
          </article>
        ))}
      </div>
    </PageShell>
  )
}

function Select({
  label,
  value,
  onChange,
  options,
  labels,
}: {
  label: string
  value: string
  onChange: (v: string) => void
  options: string[]
  labels?: Record<string, string>
}) {
  return (
    <label className="text-sm text-muted">
      {label}
      <select
        className="mt-1 w-full rounded-xl bg-bg border border-border px-3 py-2 text-foreground min-h-11"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {labels?.[opt] ?? (opt || 'Any')}
          </option>
        ))}
      </select>
    </label>
  )
}
