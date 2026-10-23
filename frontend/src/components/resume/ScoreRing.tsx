import { useEffect, useState } from 'react'
import { usePrefersReducedMotion } from '@/hooks/useMedia'

export function ScoreRing({ value }: { value: number }) {
  const reduced = usePrefersReducedMotion()
  const [shown, setShown] = useState(reduced ? value : 0)
  useEffect(() => {
    if (reduced) {
      setShown(value)
      return
    }
    setShown(0)
    const start = performance.now()
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / 1100)
      setShown(Math.round(value * t))
      if (t < 1) requestAnimationFrame(tick)
    }
    const id = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(id)
  }, [value, reduced])

  const r = 54
  const c = 2 * Math.PI * r
  const offset = c - (shown / 100) * c

  return (
    <div className="relative grid place-items-center">
      <svg width="160" height="160" viewBox="0 0 140 140" aria-hidden>
        <circle cx="70" cy="70" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="10" />
        <circle
          cx="70"
          cy="70"
          r={r}
          fill="none"
          stroke="#6ee7ff"
          strokeWidth="10"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 70 70)"
        />
      </svg>
      <div className="absolute text-center">
        <p className="font-display text-4xl">{shown}%</p>
        <p className="text-[10px] uppercase tracking-widest text-muted">Resume Match Score</p>
      </div>
    </div>
  )
}
