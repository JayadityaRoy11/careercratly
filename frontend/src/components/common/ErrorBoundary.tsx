import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import { AlertOctagon, Home, RefreshCw } from 'lucide-react'

interface Props {
  children?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false, error: null }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Unhandled application error caught by ErrorBoundary:', error, errorInfo)
  }

  private handleReload = () => {
    window.location.reload()
  }

  private handleGoHome = () => {
    window.location.href = '/'
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-bg flex items-center justify-center p-4">
          <div className="glass p-8 rounded-2xl max-w-md w-full text-center space-y-4">
            <div className="w-16 h-16 bg-danger/15 text-danger rounded-full flex items-center justify-center mx-auto">
              <AlertOctagon className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-display">Something went wrong</h2>
              <p className="text-sm text-muted mt-1">Reload the page or return home.</p>
            </div>
            {this.state.error ? (
              <div className="bg-black/40 text-muted p-3 rounded-xl text-xs font-mono text-left max-h-32 overflow-y-auto">
                {this.state.error.toString()}
              </div>
            ) : null}
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={this.handleReload}
                className="flex-1 py-2.5 px-4 bg-white/10 hover:bg-white/15 font-medium text-xs rounded-xl cursor-pointer inline-flex items-center justify-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Reload
              </button>
              <button
                type="button"
                onClick={this.handleGoHome}
                className="flex-1 py-2.5 px-4 bg-primary text-bg font-medium text-xs rounded-xl cursor-pointer inline-flex items-center justify-center gap-1.5"
              >
                <Home className="w-3.5 h-3.5" /> Home
              </button>
            </div>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
