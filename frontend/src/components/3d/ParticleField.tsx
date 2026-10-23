import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { usePrefersReducedMotion } from '@/hooks/useMedia'

export function ParticleField({ count = 90 }: { count?: number }) {
  const reduced = usePrefersReducedMotion()
  const mesh = useRef<THREE.InstancedMesh>(null)
  const dummy = useMemo(() => new THREE.Object3D(), [])
  const seeds = useMemo(
    () =>
      Array.from({ length: count }, (_, i) => {
        const n = ((i + 1) * 16807) % 2147483647
        const r = n / 2147483647
        const r2 = ((i + 3) * 48271) % 2147483647 / 2147483647
        const r3 = ((i + 5) * 69621) % 2147483647 / 2147483647
        return {
          x: (r - 0.5) * 8,
          y: (r2 - 0.5) * 5,
          z: (r3 - 0.5) * 6,
          s: 0.015 + r * 0.03,
          p: r2 * Math.PI * 2,
        }
      }),
    [count],
  )

  useFrame((state) => {
    if (!mesh.current) return
    const t = reduced ? 0 : state.clock.elapsedTime * 0.15
    seeds.forEach((p, i) => {
      dummy.position.set(p.x, p.y + Math.sin(t + p.p) * 0.15, p.z)
      dummy.scale.setScalar(p.s)
      dummy.updateMatrix()
      mesh.current!.setMatrixAt(i, dummy.matrix)
    })
    mesh.current.instanceMatrix.needsUpdate = true
  })

  return (
    <instancedMesh ref={mesh} args={[undefined, undefined, count]}>
      <sphereGeometry args={[1, count < 40 ? 6 : 8, count < 40 ? 6 : 8]} />
      <meshBasicMaterial color="#6ee7ff" transparent opacity={0.45} />
    </instancedMesh>
  )
}
