import { Canvas } from '@react-three/fiber'
import { Suspense } from 'react'
import { CareerCore } from '@/components/3d/CareerCore'
import { ParticleField } from '@/components/3d/ParticleField'
import { useIsMobile, useIsTablet, usePrefersReducedMotion } from '@/hooks/useMedia'

export function HeroCanvas() {
  const mobile = useIsMobile()
  const tablet = useIsTablet()
  const reduced = usePrefersReducedMotion()
  const particles = mobile ? 24 : tablet ? 48 : 90
  const dpr = mobile ? 1 : tablet ? 1.25 : ([1, 1.5] as [number, number])
  return (
    <Canvas
      className="h-full w-full"
      camera={{ position: [0, 0, mobile ? 6.1 : 5.2], fov: mobile ? 48 : 42 }}
      dpr={dpr}
      gl={{ antialias: !mobile, powerPreference: 'high-performance' }}
      frameloop={reduced ? 'demand' : 'always'}
    >
      <color attach="background" args={['#07080d']} />
      <ambientLight intensity={0.45} />
      <directionalLight position={[3, 4, 2]} intensity={1.1} />
      <Suspense fallback={null}>
        <CareerCore motionScale={reduced ? 0 : mobile ? 0.28 : tablet ? 0.55 : 1} />
        <ParticleField count={reduced ? 12 : particles} />
      </Suspense>
    </Canvas>
  )
}
