import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ScoreRing } from '@/components/resume/ScoreRing'
import { Button } from '@/components/ui/button'
import type { CourseRecommendResponse, ProjectResourcesResponse, ResumeAnalyzeResponse } from '@/types'

const TABS = [
  'Summary',
  'Sections',
  'Skills',
  'Keywords',
  'Experience',
  'Projects',
  'Alignment',
  'Learning',
  'Roadmap',
] as const

export function AnalysisDashboard({
  analysis,
  courses,
  projects,
}: {
  analysis: ResumeAnalyzeResponse
  courses: CourseRecommendResponse | null
  projects: ProjectResourcesResponse | null
}) {
  const [tab, setTab] = useState<(typeof TABS)[number]>('Summary')
  const intel = analysis.intelligence
  const overview = intel?.overview
  const alignment = intel?.alignment

  return (
    <div className="mt-10 space-y-6">
      <div className="glass rounded-3xl p-6 sm:p-8 flex flex-col lg:flex-row items-center gap-8">
        <ScoreRing value={analysis.score} />
        <div className="min-w-0">
          <p className="font-display text-2xl sm:text-3xl">{analysis.target_role}</p>
          <p className="text-sm text-muted mt-2">{analysis.disclaimer}</p>
          {overview ? <p className="mt-3 text-sm">{overview.what_is_good}</p> : null}
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
        {TABS.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setTab(item)}
            className={`shrink-0 rounded-full px-4 py-2 text-sm cursor-pointer min-h-11 ${
              tab === item ? 'bg-primary text-bg' : 'bg-white/5 text-muted'
            }`}
          >
            {item}
          </button>
        ))}
      </div>

      {tab === 'Summary' ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Note title="What is good" body={overview?.what_is_good || analysis.strengths.join(' ')} />
          <Note title="Why it is good" body={overview?.why_it_is_good || 'Coverage is based on explicit skill mentions, not inferred prestige.'} />
          <Note title="What is missing" body={overview?.what_is_missing || analysis.missing_skills.join(', ') || 'No required skills were missing from extraction.'} />
          <Note title="Why it matters" body={overview?.why_it_matters || 'Role profiles weight required skills most heavily in the Resume Match Score.'} />
          <Note title="What to change" body={overview?.what_to_change || analysis.improvements.join(' ')} />
          <Note title="How to change" body={overview?.how_to_change || 'Add genuine bullets with action, technology, task, and a real result if you have one. Do not invent metrics.'} />
          <Chips title="Skills to learn (only if genuine)" items={overview?.skills_to_learn || analysis.missing_skills} />
          <Chips title="Project ideas" items={overview?.project_ideas || analysis.recommended_project_themes} />
        </div>
      ) : null}

      {tab === 'Sections' ? (
        <div className="grid gap-3 md:grid-cols-2">
          {(intel?.section_reviews || []).map((section) => (
            <article key={section.name} className="glass rounded-2xl p-5">
              <div className="flex justify-between gap-3">
                <p className="font-display capitalize">{section.name}</p>
                <p className="text-primary">{section.score}/100 · {section.status}</p>
              </div>
              <List label="Strengths" items={section.strengths} />
              <List label="Issues" items={section.issues} />
              <List label="Improvements" items={section.improvements} />
            </article>
          ))}
        </div>
      ) : null}

      {tab === 'Skills' ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Chips title="Matched" items={analysis.matched_skills} tone="success" />
          <Chips title="Missing (add only if genuine)" items={analysis.missing_skills} tone="danger" />
          <Chips title="Extracted" items={analysis.extracted_skills} />
          <Chips title="Partial" items={analysis.partial_matches.map((p) => `${p.skill} ← ${p.related_found}`)} tone="warning" />
        </div>
      ) : null}

      {tab === 'Keywords' && intel?.keyword_gap ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Chips title="Detected" items={intel.keyword_gap.detected} tone="success" />
          <Chips title="Missing" items={intel.keyword_gap.missing} tone="danger" />
          <Chips title="Weakly represented" items={intel.keyword_gap.weak} tone="warning" />
          <div className="glass rounded-2xl p-5 md:col-span-2">
            <p className="text-sm text-muted mb-2">Recommended placement</p>
            {(intel.keyword_gap.placement || []).map((row) => (
              <p key={row.skill} className="text-sm py-1 border-b border-border last:border-0">
                {row.advice}
              </p>
            ))}
          </div>
        </div>
      ) : null}

      {tab === 'Experience' && intel?.bullet_analysis ? (
        <div className="space-y-3">
          <p className="text-sm text-muted">{intel.bullet_analysis.guidance}</p>
          {intel.bullet_analysis.items.map((bullet) => (
            <article key={bullet.text} className="glass rounded-2xl p-4">
              <p className="text-sm">{bullet.text}</p>
              <p className="text-xs text-warning mt-2">Problem: {bullet.problem}</p>
              <p className="text-xs text-muted mt-1">Suggested structure: {bullet.suggested_structure}</p>
            </article>
          ))}
        </div>
      ) : null}

      {tab === 'Projects' ? (
        <div className="grid gap-3">
          {(intel?.projects_analysis || []).length === 0 ? (
            <p className="text-muted text-sm">No project blocks detected. Add a Projects heading if you have real work.</p>
          ) : (
            intel?.projects_analysis.map((project) => (
              <article key={project.title} className="glass rounded-2xl p-5">
                <p className="font-display">{project.title}</p>
                <p className="text-xs text-muted mt-1">Detected skills: {project.detected_skills.join(', ') || '—'}</p>
                <List label="Missing information" items={project.missing_information} />
                <List label="Recommendations" items={project.recommendations} />
              </article>
            ))
          )}
        </div>
      ) : null}

      {tab === 'Alignment' && alignment ? (
        <div className="grid gap-3 md:grid-cols-2">
          {Object.entries(alignment)
            .sort(([a], [b]) => (a === 'overall_score' ? -1 : b === 'overall_score' ? 1 : 0))
            .map(([key, value]) => (
            <article key={key} className="glass rounded-2xl p-5">
              <p className="text-sm capitalize">{key.replaceAll('_', ' ')}</p>
              <div className="h-2 rounded-full bg-white/10 mt-2 overflow-hidden">
                <div className="h-full bg-primary" style={{ width: `${value.score}%` }} />
              </div>
              <p className="text-primary text-sm mt-1">{value.score}%</p>
              <p className="text-xs text-muted mt-2">{value.explanation}</p>
            </article>
          ))}
        </div>
      ) : null}

      {tab === 'Learning' ? (
        <div className="space-y-6">
          {(courses?.recommendations || []).map((group) => (
            <div key={group.skill} className="glass rounded-2xl p-5">
              <p className="font-display">{group.skill}</p>
              <p className="text-xs text-muted mb-3">
                Learn this only if you intend to use it. Add the keyword after you have genuine experience.
              </p>
              <div className="grid sm:grid-cols-3 gap-3">
                {group.courses.map((course) => (
                  <a
                    key={course.id}
                    href={course.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="rounded-xl border border-border p-3 min-h-11"
                  >
                    <p className="text-sm">{course.title}</p>
                    <p className="text-xs text-muted">{course.provider}</p>
                  </a>
                ))}
              </div>
            </div>
          ))}
          <div>
            <h3 className="font-display text-xl mb-3">Make your project stronger</h3>
            <div className="grid md:grid-cols-2 gap-3">
              {(projects?.resources || []).map((res) => (
                <a
                  key={res.url}
                  href={res.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="glass rounded-2xl p-4 flex justify-between gap-3"
                >
                  <div>
                    <p className="text-xs uppercase text-primary">{res.type}</p>
                    <p className="font-display">{res.title}</p>
                    <p className="text-xs text-muted">{res.source}</p>
                  </div>
                  <span className="text-sm text-primary shrink-0">Open Resource ↗</span>
                </a>
              ))}
            </div>
          </div>
        </div>
      ) : null}

      {tab === 'Roadmap' && intel?.roadmap ? (
        <div className="grid gap-4 lg:grid-cols-3">
          <RoadCol title="High priority" items={intel.roadmap.high} />
          <RoadCol title="Medium priority" items={intel.roadmap.medium} />
          <RoadCol title="Optional" items={intel.roadmap.optional} />
        </div>
      ) : null}

      <p className="text-xs text-muted">{intel?.metric_policy}</p>
      <Link to="/job-portal">
        <Button variant="secondary">Match this resume to jobs</Button>
      </Link>
    </div>
  )
}

function Note({ title, body }: { title: string; body: string }) {
  return (
    <div className="glass rounded-2xl p-5">
      <p className="text-xs uppercase tracking-widest text-muted">{title}</p>
      <p className="mt-2 text-sm">{body}</p>
    </div>
  )
}

function List({ label, items }: { label: string; items: string[] }) {
  if (!items.length) return null
  return (
    <div className="mt-3">
      <p className="text-xs text-muted">{label}</p>
      <ul className="mt-1 space-y-1 text-sm">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  )
}

function Chips({ title, items, tone = 'primary' }: { title: string; items: string[]; tone?: string }) {
  const colors: Record<string, string> = {
    primary: 'border-primary/30 text-primary',
    success: 'border-success/40 text-success',
    danger: 'border-danger/40 text-danger',
    warning: 'border-warning/40 text-warning',
  }
  return (
    <div className="glass rounded-2xl p-5">
      <p className="text-sm text-muted mb-3">{title}</p>
      <div className="flex flex-wrap gap-2">
        {items.length ? (
          items.map((item) => (
            <span key={item} className={`rounded-full border px-3 py-1 text-xs ${colors[tone] || colors.primary}`}>
              {item}
            </span>
          ))
        ) : (
          <span className="text-sm text-muted">None listed</span>
        )}
      </div>
    </div>
  )
}

function RoadCol({
  title,
  items,
}: {
  title: string
  items: { issue: string; why: string; what: string; benefit: string }[]
}) {
  return (
    <div className="glass rounded-2xl p-5">
      <p className="font-display">{title}</p>
      <div className="mt-3 space-y-3">
        {items.map((item) => (
          <div key={item.issue} className="border-b border-border pb-3 last:border-0">
            <p className="text-sm">{item.issue}</p>
            <p className="text-xs text-muted mt-1">{item.why}</p>
            <p className="text-xs mt-1">{item.what}</p>
            <p className="text-xs text-primary mt-1">{item.benefit}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
