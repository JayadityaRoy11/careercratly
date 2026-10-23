export function Background() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-bg" />
      <div className="absolute inset-0 grid-overlay opacity-40" />
      <div className="absolute -top-32 left-1/4 size-[32rem] rounded-full bg-secondary/20 blur-[120px]" />
      <div className="absolute bottom-0 right-0 size-[28rem] rounded-full bg-primary/10 blur-[110px]" />
    </div>
  )
}
