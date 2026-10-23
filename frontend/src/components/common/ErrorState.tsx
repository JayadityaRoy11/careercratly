import { AlertTriangle, FileQuestion, Loader2 } from 'lucide-react'
import { cn } from '@/lib/cn'

export function LoadingState({
  title,
  detail,
  className,
}: {
  title: string
  detail?: string
  className?: string
}) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={cn('glass rounded-2xl p-8 flex flex-col items-center text-center gap-3', className)}
    >
      <Loader2 className="size-8 text-primary animate-spin" />
      <p className="font-display text-lg">{title}</p>
      {detail ? <p className="text-sm text-muted max-w-md">{detail}</p> : null}
    </div>
  )
}

export function ErrorState({
  title = 'Something went wrong',
  message,
  onRetry,
}: {
  title?: string
  message: string
  onRetry?: () => void
}) {
  return (
    <div role="alert" className="glass rounded-2xl p-8 flex flex-col items-center text-center gap-3">
      <AlertTriangle className="size-8 text-danger" />
      <p className="font-display text-lg">{title}</p>
      <p className="text-sm text-muted max-w-md">{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-2 text-sm text-primary underline cursor-pointer"
        >
          Try again
        </button>
      ) : null}
    </div>
  )
}

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="glass rounded-2xl p-8 flex flex-col items-center text-center gap-3">
      <FileQuestion className="size-8 text-muted" />
      <p className="font-display text-lg">{title}</p>
      <p className="text-sm text-muted max-w-md">{message}</p>
    </div>
  )
}
