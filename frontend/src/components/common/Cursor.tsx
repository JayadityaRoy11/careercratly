import { useEffect, useState } from 'react'
import { usePrefersReducedMotion, useIsMobile } from '@/hooks/useMedia'

export function Cursor() {
  const reduced = usePrefersReducedMotion()
  const mobile = useIsMobile()
  const [pos, setPos] = useState({ x: -100, y: -100 })

  useEffect(() => {
    if (reduced || mobile) return
    const move = (e: MouseEvent) => setPos({ x: e.clientX, y: e.clientY })
    window.addEventListener('pointermove', move)
    return () => window.removeEventListener('pointermove', move)
  }, [reduced, mobile])

  if (reduced || mobile) return null

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed z-[80] size-8 rounded-full border border-primary/50 mix-blend-difference hidden md:block"
      style={{ left: pos.x - 16, top: pos.y - 16, transition: 'transform 80ms linear' }}
    />
  )
}
