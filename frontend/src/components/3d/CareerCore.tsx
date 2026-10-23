import { Html, Line } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useMemo, useRef } from 'react'
import type { Group } from 'three'
import { usePrefersReducedMotion } from '@/hooks/useMedia'

const NODES = [
  { label: 'RESUME', pos: [1.8, 0.9, 0.2] as const },
  { label: 'SKILLS', pos: [-1.7, 1.0, 0.4] as const },
  { label: 'JOBS', pos: [1.5, -1.0, 0.5] as const },
  { label: 'LEARNING', pos: [-1.6, -0.85, 0.3] as const },
  { label: 'INTERVIEW', pos: [0.1, 1.55, -0.4] as const },
]

export function CareerCore({ motionScale = 1 }: { motionScale?: number }) {
  const group = useRef<Group>(null)
  const reduced = usePrefersReducedMotion()
  const lines = useMemo(
    () => NODES.map((node) => [[0, 0, 0] as [number, number, number], [...node.pos] as [number, number, number]]),
    [],
  )

  useFrame((state) => {
    if (!group.current) return
    const t = reduced ? 0 : state.clock.elapsedTime * 0.12 * motionScale
    group.current.rotation.y = t
    if (!reduced) {
      group.current.rotation.x = state.pointer.y * 0.18 * motionScale
      group.current.rotation.z = state.pointer.x * 0.08 * motionScale
    }
  })

  return (
    <group ref={group}>
      <mesh>
        <icosahedronGeometry args={[0.58, motionScale < 0.4 ? 0 : 1]} />
        <meshStandardMaterial
          color="#8b7cff"
          emissive="#4c1d95"
          emissiveIntensity={1.1}
          metalness={0.4}
          roughness={0.25}
          wireframe
        />
      </mesh>
      <mesh>
        <sphereGeometry args={[0.28, 24, 24]} />
        <meshStandardMaterial color="#6ee7ff" emissive="#22d3ee" emissiveIntensity={1.4} />
      </mesh>
      {lines.map((pts, i) => (
        <Line key={i} points={pts} color="#6ee7ff" lineWidth={1} transparent opacity={0.45} />
      ))}
      {NODES.map((node) => (
        <group key={node.label} position={node.pos}>
          <mesh>
            <sphereGeometry args={[0.09, 16, 16]} />
            <meshStandardMaterial color="#c084fc" emissive="#7c3aed" emissiveIntensity={0.9} />
          </mesh>
          <Html center distanceFactor={8} style={{ pointerEvents: 'none' }}>
            <div className="text-[10px] tracking-widest text-white/90 whitespace-nowrap">{node.label}</div>
          </Html>
        </group>
      ))}
    </group>
  )
}
