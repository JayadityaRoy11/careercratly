import { Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/cn'

const LINKS = [
  { to: '/', label: 'Home' },
  { to: '/resume-analyzer', label: 'Resume Analyzer' },
  { to: '/job-portal', label: 'Job Portal' },
  { to: '/interview-prep', label: 'Interview Prep' },
  { to: '/about', label: 'About' },
]

export function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={cn(
        'sticky top-0 z-50 transition-colors duration-300',
        scrolled ? 'glass' : 'bg-transparent',
      )}
    >
      <div className="mx-auto flex w-full max-w-[90rem] items-center justify-between gap-3 px-4 py-3 sm:px-6 lg:px-10">
        <Link to="/" className="flex items-center gap-2">
          <span className="grid size-8 place-items-center rounded-lg bg-primary/15 text-primary font-display text-xs">
            CC
          </span>
          <span className="font-display text-sm tracking-wide">CareerCratly.AI</span>
        </Link>
        <nav className="hidden lg:flex items-center gap-5 xl:gap-6 text-sm text-muted" aria-label="Primary">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                cn('hover:text-foreground transition', isActive && 'text-primary')
              }
              end={link.to === '/'}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="hidden lg:block">
          <Link to="/resume-analyzer">
            <Button size="sm">Analyze Resume</Button>
          </Link>
        </div>
        <button
          type="button"
          className="lg:hidden p-2 min-h-11 min-w-11 cursor-pointer"
          aria-label={open ? 'Close menu' : 'Open menu'}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X /> : <Menu />}
        </button>
      </div>
      {open ? (
        <div className="lg:hidden glass border-t px-4 py-4 flex flex-col gap-3">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className="text-sm py-2"
              end={link.to === '/'}
              onClick={() => setOpen(false)}
            >
              {link.label}
            </NavLink>
          ))}
          <Link to="/resume-analyzer">
            <Button className="w-full">Analyze Resume</Button>
          </Link>
        </div>
      ) : null}
    </header>
  )
}
