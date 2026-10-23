import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { usePrefersReducedMotion } from '@/hooks/useMedia'

export function SmoothScroll({ children }: { children: React.ReactNode }) {
  const reduced = usePrefersReducedMotion()
  const location = useLocation()

  useEffect(() => {
    if (reduced) return
    let raf = 0
    let lenis: { raf: (t: number) => void; destroy: () => void; scrollTo: (y: number) => void } | null = null
    let cancelled = false

    void import('lenis').then(({ default: Lenis }) => {
      if (cancelled) return
      const instance = new Lenis({ duration: 1.1, smoothWheel: true })
      lenis = instance
      const loop = (time: number) => {
        instance.raf(time)
        raf = requestAnimationFrame(loop)
      }
      raf = requestAnimationFrame(loop)
    })

    return () => {
      cancelled = true
      cancelAnimationFrame(raf)
      lenis?.destroy()
    }
  }, [reduced])

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location.pathname])

  return <>{children}</>
}
