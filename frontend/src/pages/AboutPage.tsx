import { Link } from 'react-router-dom'
import { PageShell } from '@/components/layout/PageShell'
import { Reveal } from '@/components/animations/Reveal'
import { Button } from '@/components/ui/button'

const STEPS = [
  { title: 'Resume', body: 'Upload PDF or DOCX. We extract text — nothing is executed.' },
  { title: 'Skill extraction', body: 'A taxonomy matcher finds skills, aliases, and abbreviations.' },
  { title: 'Role analysis', body: 'An explainable Resume Match Score vs a target role.' },
  { title: 'Job matching', body: 'Demo jobs ranked by overlap. Open the original listing.' },
  { title: 'Learning', body: 'Courses and project links for missing skills.' },
  { title: 'Interview', body: 'Questions and text evaluation. Camera is optional.' },
]

export function AboutPage() {
  return (
    <PageShell>
      <p className="text-xs uppercase tracking-[0.28em] text-primary">CareerCratly.AI</p>
      <h1 className="font-display text-4xl sm:text-6xl mt-3">A career system, not a form.</h1>
      <p className="text-muted mt-4 max-w-2xl">
        CareerCratly.AI connects resume text to roles, gaps, learning, and interview practice.
        There are no accounts and no scraped job boards.
      </p>
      <div className="mt-12 space-y-4">
        {STEPS.map((step, i) => (
          <Reveal key={step.title} className="glass rounded-2xl p-6 flex gap-6 items-start">
            <span className="font-display text-primary text-2xl">0{i + 1}</span>
            <div>
              <h2 className="font-display text-2xl">{step.title}</h2>
              <p className="text-muted mt-1">{step.body}</p>
            </div>
          </Reveal>
        ))}
      </div>
      <Link to="/resume-analyzer" className="inline-block mt-10">
        <Button size="lg">Start with a resume</Button>
      </Link>
    </PageShell>
  )
}
