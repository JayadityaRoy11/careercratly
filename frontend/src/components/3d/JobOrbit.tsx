import { Html } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import type { Group } from 'three'
import { usePrefersReducedMotion } from '@/hooks/useMedia'

const JOBS = [
  { title: 'AI Engineer', match: 92 },
  { title: 'Data Scientist', match: 88 },
  { title: 'Backend Developer', match: 81 },
  { title: 'Data Analyst', match: 76 },
]

export function JobOrbit() {
  const ref = useRef<Group>(null)
  const reduced = usePrefersReducedMotion()
  useFrame((s) => {
    if (ref.current && !reduced) ref.current.rotation.y = s.clock.elapsedTime * 0.25
  })
  return (
    <group ref={ref}>
      {JOBS.map((job, i) => {
        const a = (i / JOBS.length) * Math.PI * 2
        return (
          <Html key={job.title} position={[Math.cos(a) * 1.6, Math.sin(a * 1.2) * 0.5, Math.sin(a) * 1.6]} center>
            <div className="glass rounded-xl px-3 py-2 text-[11px] w-36 text-left">
              <p className="font-display text-foreground">{job.title}</p>
              <p className="text-primary">{job.match}% Resume Match</p>
            </div>
          </Html>
        )
      })}
    </group>
  )
}
