import { Line } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import type { Group } from 'three'
import { usePrefersReducedMotion } from '@/hooks/useMedia'

export function SkillNetwork() {
  const ref = useRef<Group>(null)
  const reduced = usePrefersReducedMotion()
  useFrame((s) => {
    if (ref.current && !reduced) ref.current.rotation.y = s.clock.elapsedTime * 0.2
  })
  return (
    <group ref={ref}>
      <Line points={[[-1, 0, 0], [1, 0.4, 0], [0.2, -0.8, 0.4]]} color="#8b7cff" />
      <Line points={[[-0.6, 0.7, 0], [0.8, -0.3, 0.2]]} color="#6ee7ff" />
      {[[-1, 0, 0], [1, 0.4, 0], [0.2, -0.8, 0.4], [-0.6, 0.7, 0]].map((p) => (
        <mesh key={p.join(',')} position={p as [number, number, number]}>
          <sphereGeometry args={[0.07, 12, 12]} />
          <meshStandardMaterial color="#6ee7ff" emissive="#0891b2" emissiveIntensity={0.8} />
        </mesh>
      ))}
    </group>
  )
}
