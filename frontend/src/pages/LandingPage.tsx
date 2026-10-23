import { lazy, Suspense } from 'react'
import { Link } from 'react-router-dom'
import { Reveal } from '@/components/animations/Reveal'
import { Button } from '@/components/ui/button'

const HeroCanvas = lazy(() =>
  import('@/components/3d/HeroCanvas').then((m) => ({ default: m.HeroCanvas })),
)

const FLOW = ['Resume', 'Analyze', 'Match', 'Improve', 'Prepare']

const PREVIEW_JOBS = [
  { title: 'AI Engineer', match: 92, location: 'Bengaluru', mode: 'Hybrid', type: 'Full-time' },
  { title: 'Data Scientist', match: 88, location: 'Remote', mode: 'Remote', type: 'Full-time' },
  { title: 'Backend Developer', match: 81, location: 'Pune', mode: 'On-site', type: 'Internship' },
  { title: 'Data Analyst', match: 76, location: 'Mumbai', mode: 'Hybrid', type: 'Full-time' },
]

export function LandingPage() {
  return (
    <div className="w-full overflow-x-clip">
      <section className="relative w-full min-h-[calc(100svh-4.5rem)] grid items-center gap-8 px-4 py-8 sm:px-8 lg:grid-cols-2 lg:gap-12 lg:px-12 xl:px-20">
        <div className="max-w-2xl">
          <p className="text-xs uppercase tracking-[0.3em] text-primary">CareerCratly.AI</p>
          <h1 className="font-display mt-4 text-[clamp(2.1rem,5vw,4.75rem)] leading-[0.95]">
            TURN YOUR RESUME
            <br />
            INTO YOUR NEXT
            <br />
            OPPORTUNITY.
          </h1>
          <p className="mt-5 max-w-xl text-muted text-[0.95rem] sm:text-base">
            Your resume is data. Your career is a system. Analyze alignment, discover roles, close
            skill gaps, and rehearse interviews — in one workspace.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/resume-analyzer">
              <Button size="lg">Analyze My Resume</Button>
            </Link>
            <Link to="/job-portal">
              <Button size="lg" variant="secondary">
                Explore Job Portal
              </Button>
            </Link>
          </div>
        </div>
        <div className="relative h-[240px] sm:h-[340px] lg:h-[min(70vh,640px)] w-full rounded-3xl overflow-hidden border border-border">
          <Suspense
            fallback={<div className="h-full grid place-items-center text-muted text-sm">Initializing core…</div>}
          >
            <HeroCanvas />
          </Suspense>
        </div>
      </section>

      <section className="w-full px-4 sm:px-8 lg:px-12 xl:px-20 py-16 sm:py-20">
        <div className="mx-auto max-w-[90rem]">
        <Reveal>
          <h2 className="font-display text-3xl sm:text-5xl">ONE RESUME. MULTIPLE POSSIBILITIES.</h2>
          <p className="mt-3 text-muted max-w-2xl">A linear system, not a pile of tools.</p>
        </Reveal>
        <div className="mt-10 grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-5">
          {FLOW.map((step, i) => (
            <Reveal key={step} delay={i * 0.08} className="glass rounded-2xl p-5">
              <p className="text-xs text-primary">0{i + 1}</p>
              <p className="font-display mt-2 text-xl">{step}</p>
            </Reveal>
          ))}
        </div>
        </div>
      </section>

      <section className="w-full px-4 sm:px-8 lg:px-12 xl:px-20 py-16">
        <div className="mx-auto max-w-[90rem]">
        <Reveal>
          <h2 className="font-display text-3xl">Resume Intelligence</h2>
        </Reveal>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            ['Resume Match Score', '82'],
            ['Matched', 'Python · SQL · FastAPI'],
            ['Missing', 'Kubernetes · MLOps'],
            ['Recommended', 'Docker · AWS'],
          ].map(([k, v]) => (
            <Reveal key={k} className="glass rounded-2xl p-6">
              <p className="text-xs uppercase tracking-widest text-muted">{k}</p>
              <p className="mt-3 font-display text-2xl text-primary">{v}</p>
            </Reveal>
          ))}
        </div>
        </div>
      </section>

      <section className="w-full px-4 sm:px-8 lg:px-12 xl:px-20 py-16">
        <div className="mx-auto max-w-[90rem]">
        <Reveal>
          <h2 className="font-display text-3xl">Job Intelligence</h2>
        </Reveal>
        <div className="mt-8 grid gap-4 grid-cols-1 sm:grid-cols-2 xl:grid-cols-4">
          {PREVIEW_JOBS.map((job) => (
            <Reveal key={job.title} className="glass rounded-2xl p-5 hover:-translate-y-1 transition">
              <p className="font-display text-lg">{job.title}</p>
              <p className="text-primary text-sm mt-1">{job.match}% Resume Match</p>
              <p className="text-xs text-muted mt-3">
                {job.location} · {job.mode} · {job.type}
              </p>
            </Reveal>
          ))}
        </div>
        </div>
      </section>

      <section className="w-full px-4 sm:px-8 lg:px-12 xl:px-20 py-16">
        <div className="mx-auto max-w-[90rem] grid grid-cols-1 md:grid-cols-3 gap-4">
        {['Current Skills', 'Missing Skills', 'Recommended Learning'].map((title) => (
          <Reveal key={title} className="glass rounded-2xl p-6 min-h-40">
            <p className="font-display text-xl">{title}</p>
            <p className="text-sm text-muted mt-2">Connected through the same skill taxonomy the analyzer uses.</p>
          </Reveal>
        ))}
        </div>
      </section>

      <section className="w-full px-4 sm:px-8 lg:px-12 xl:px-20 py-16">
        <div className="mx-auto max-w-[90rem]">
        <Reveal className="glass rounded-3xl p-6 sm:p-8 grid md:grid-cols-2 gap-8 items-center">
          <div>
            <h2 className="font-display text-3xl">Interview Preparation</h2>
            <p className="text-muted mt-3">
              Camera optional. Evaluation is text-based: relevance, keywords, structure — never
              personality or emotion.
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-bg p-4 text-sm">
            <p className="text-muted">Question</p>
            <p className="mt-2">How would you design pagination for a FastAPI list endpoint?</p>
            <div className="mt-4 h-10 rounded-full bg-white/5 overflow-hidden">
              <div className="h-full w-2/3 bg-primary/40" />
            </div>
          </div>
        </Reveal>
        </div>
      </section>

      <section className="w-full px-4 sm:px-8 lg:px-12 xl:px-20 py-20 sm:py-24 text-center">
        <div className="mx-auto max-w-4xl">
        <h2 className="font-display text-3xl sm:text-5xl">YOUR NEXT ROLE STARTS WITH WHAT YOU ALREADY KNOW.</h2>
        <Link to="/resume-analyzer" className="inline-block mt-8">
          <Button size="lg">START ANALYZING</Button>
        </Link>
        </div>
      </section>
    </div>
  )
}
