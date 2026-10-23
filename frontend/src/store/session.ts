import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ResumeAnalyzeResponse, ResumeUploadResponse } from '@/types'

interface SessionState {
  resume: ResumeUploadResponse | null
  analysis: ResumeAnalyzeResponse | null
  targetRole: string
  setResume: (resume: ResumeUploadResponse | null) => void
  setAnalysis: (analysis: ResumeAnalyzeResponse | null) => void
  setTargetRole: (role: string) => void
  reset: () => void
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set) => ({
      resume: null,
      analysis: null,
      targetRole: 'Backend Developer',
      setResume: (resume) => set({ resume, analysis: null }),
      setAnalysis: (analysis) => set({ analysis }),
      setTargetRole: (targetRole) => set({ targetRole }),
      reset: () => set({ resume: null, analysis: null, targetRole: 'Backend Developer' }),
    }),
    {
      name: 'careercratly-session',
      partialize: (state) => ({
        resume: state.resume
          ? {
              ...state.resume,
              text: state.resume.text.slice(0, 4000),
            }
          : null,
        analysis: state.analysis,
        targetRole: state.targetRole,
      }),
    },
  ),
)
