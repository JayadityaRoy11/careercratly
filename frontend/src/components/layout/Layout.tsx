import { Outlet } from 'react-router-dom'
import { Background } from '@/components/layout/Background'
import { Navbar } from '@/components/layout/Navbar'
import { SmoothScroll } from '@/components/layout/SmoothScroll'

export function Layout() {
  return (
    <SmoothScroll>
      <Background />
      <div className="min-h-svh flex flex-col overflow-x-clip">
        <Navbar />
        <main className="flex-1">
          <Outlet />
        </main>
        <footer className="border-t border-border py-8 text-center text-xs text-muted">
          CareerCratly.AI · academic prototype · mock jobs · no accounts · {new Date().getFullYear()}
        </footer>
      </div>
    </SmoothScroll>
  )
}
