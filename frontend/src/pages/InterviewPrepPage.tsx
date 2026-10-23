import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { ErrorState, LoadingState } from '@/components/common/ErrorState'
import { PageShell } from '@/components/layout/PageShell'
import { INTERVIEW_ROLES } from '@/data/roles'
import { evaluateInterviewAnswer, getInterviewQuestions, parseApiError } from '@/lib/api'
import type { InterviewEvaluateResponse, InterviewQuestion } from '@/types'

export function InterviewPrepPage() {
  const [role, setRole] = useState('Backend Developer')
  const [difficulty, setDifficulty] = useState('medium')
  const [questions, setQuestions] = useState<InterviewQuestion[]>([])
  const [index, setIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<InterviewEvaluateResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [camError, setCamError] = useState<string | null>(null)
  const [live, setLive] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const load = async () => {
    setBusy(true)
    setError(null)
    setResult(null)
    try {
      const data = await getInterviewQuestions(role, difficulty)
      setQuestions(data.questions)
      setIndex(0)
      setAnswer('')
    } catch (err) {
      setError(parseApiError(err).message)
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    let active = true
    const run = async () => {
      setBusy(true)
      setError(null)
      setResult(null)
      try {
        const data = await getInterviewQuestions(role, difficulty)
        if (!active) return
        setQuestions(data.questions)
        setIndex(0)
        setAnswer('')
      } catch (err) {
        if (active) setError(parseApiError(err).message)
      } finally {
        if (active) setBusy(false)
      }
    }
    void run()
    return () => {
      active = false
      streamRef.current?.getTracks().forEach((t) => t.stop())
      streamRef.current = null
    }
  }, [role, difficulty])

  const stopMedia = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    setLive(false)
  }

  const startMedia = async () => {
    setCamError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      streamRef.current = stream
      if (videoRef.current) videoRef.current.srcObject = stream
      setLive(true)
    } catch {
      setCamError('Camera or microphone permission denied. You can still type an answer.')
    }
  }

  const question = questions[index]

  const evaluate = async () => {
    if (!question) return
    setBusy(true)
    setError(null)
    try {
      const data = await evaluateInterviewAnswer({ role, question: question.question, answer })
      setResult(data)
    } catch (err) {
      setError(parseApiError(err).message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <PageShell>
      <p className="text-xs uppercase tracking-[0.28em] text-primary">Interview simulator</p>
      <h1 className="font-display text-4xl mt-3">Practice in text. Camera is optional.</h1>
      <p className="text-muted mt-2 text-sm">No facial, personality, or psychological scoring.</p>

      <div className="mt-8 grid md:grid-cols-3 gap-3">
        <label className="text-sm">
          Role
          <select className="mt-1 w-full rounded-xl bg-bg border border-border px-3 py-2" value={role} onChange={(e) => setRole(e.target.value)}>
            {INTERVIEW_ROLES.map((r) => (
              <option key={r}>{r}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          Difficulty
          <select className="mt-1 w-full rounded-xl bg-bg border border-border px-3 py-2" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </label>
        <div className="flex items-end">
          <Button className="w-full" onClick={() => void load()} disabled={busy}>
            Load questions
          </Button>
        </div>
      </div>

      <div className="mt-8 grid lg:grid-cols-2 gap-4">
        <div className="glass rounded-3xl p-5">
          <p className="text-xs text-muted">Question</p>
          <p className="font-display text-xl mt-2">{question?.question || '—'}</p>
          <textarea
            className="mt-4 w-full min-h-40 rounded-xl bg-bg border border-border p-3"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            aria-label="Your answer"
            placeholder="Answer in complete sentences. Mention tools and structure."
          />
          <Button className="mt-3" onClick={() => void evaluate()} disabled={busy || !answer.trim()}>
            Analyze Answer
          </Button>
        </div>
        <div className="glass rounded-3xl p-5">
          <p className="text-xs text-muted">Camera preview</p>
          <video ref={videoRef} autoPlay muted playsInline className="mt-3 w-full rounded-2xl bg-black aspect-video" />
          <div className="mt-3 flex gap-2">
            {!live ? (
              <Button variant="secondary" onClick={() => void startMedia()}>
                Start camera
              </Button>
            ) : (
              <Button variant="secondary" onClick={stopMedia}>
                Stop camera
              </Button>
            )}
          </div>
          {camError ? <p className="text-sm text-warning mt-2">{camError}</p> : null}
          <div className="mt-4 h-10 rounded-full bg-white/5 overflow-hidden" aria-hidden>
            <div className={`h-full bg-primary/50 ${live ? 'w-2/3 animate-pulse' : 'w-6'}`} />
          </div>
        </div>
      </div>

      {busy ? <LoadingState className="mt-8" title="Analyzing your answer..." /> : null}
      {error ? <div className="mt-8"><ErrorState message={error} /></div> : null}

      {result ? (
        <div className="mt-10 glass rounded-3xl p-6">
          <p className="font-display text-3xl">{result.score}</p>
          <Bar label="Technical Relevance" value={result.technical_relevance} />
          <Bar label="Keyword Coverage" value={result.keyword_coverage} />
          <Bar label="Structure" value={result.structure_score} />
          <Bar label="Clarity" value={Math.round((result.structure_score + result.score) / 2)} />
          <div className="grid md:grid-cols-3 gap-4 mt-6 text-sm">
            <List title="Strengths" items={result.strengths} />
            <List title="Missing concepts" items={result.missing_keywords} />
            <List title="Suggestions" items={result.suggestions} />
          </div>
        </div>
      ) : null}
    </PageShell>
  )
}

function Bar({ label, value }: { label: string; value: number }) {
  return (
    <div className="mt-4">
      <div className="flex justify-between text-sm">
        <span>{label}</span>
        <span className="text-primary">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/10 mt-1 overflow-hidden">
        <div className="h-full bg-primary" style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <p className="text-muted text-xs uppercase">{title}</p>
      <ul className="mt-2 space-y-1">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  )
}
