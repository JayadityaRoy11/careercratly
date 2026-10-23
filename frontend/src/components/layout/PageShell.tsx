export function PageShell({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`w-full px-4 sm:px-6 lg:px-10 xl:px-16 py-8 sm:py-12 ${className}`}>
      <div className="mx-auto w-full max-w-[90rem]">{children}</div>
    </div>
  )
}
