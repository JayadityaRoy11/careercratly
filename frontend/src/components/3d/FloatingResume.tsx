import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import type { Mesh } from 'three'
import { usePrefersReducedMotion } from '@/hooks/useMedia'

export function FloatingResume() {
  const ref = useRef<Mesh>(null)
  const reduced = usePrefersReducedMotion()
  useFrame((s) => {
    if (!ref.current || reduced) return
    ref.current.rotation.y = Math.sin(s.clock.elapsedTime * 0.4) * 0.25
    ref.current.position.y = Math.sin(s.clock.elapsedTime * 0.8) * 0.12
  })
  return (
    <mesh ref={ref} rotation={[0.2, 0.4, 0.05]}>
      <boxGeometry args={[1.1, 1.45, 0.04]} />
      <meshStandardMaterial color="#151924" metalness={0.2} roughness={0.4} />
    </mesh>
  )
}
