export function InterviewScene() {
  return (
    <mesh>
      <torusGeometry args={[0.9, 0.04, 12, 48]} />
      <meshStandardMaterial color="#6ee7ff" emissive="#155e75" emissiveIntensity={0.7} />
    </mesh>
  )
}
