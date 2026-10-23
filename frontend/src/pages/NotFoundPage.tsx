import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export function NotFoundPage() {
  return (
    <div className="min-h-[60vh] grid place-items-center px-4 text-center">
      <div>
        <p className="font-display text-6xl text-primary">404</p>
        <p className="text-muted mt-2">That route is not part of the prototype.</p>
        <Link to="/" className="inline-block mt-6">
          <Button>Home</Button>
        </Link>
      </div>
    </div>
  )
}
