import axios, { AxiosError } from 'axios'
import type {
  CourseRecommendResponse,
  InterviewEvaluateResponse,
  InterviewQuestionsResponse,
  JobListResponse,
  JobMatchResponse,
  JobSearchParams,
  ProjectResourcesResponse,
  ProviderStatus,
  ResumeAnalyzeResponse,
  ResumeUploadResponse,
} from '@/types'

const root = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const API_BASE_URL = `${root.replace(/\/$/, '')}/api`

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
})

export interface ParsedApiError {
  code: string
  message: string
  details?: unknown
}

export function parseApiError(error: unknown): ParsedApiError {
  if (!axios.isAxiosError(error)) {
    return { code: 'unknown', message: error instanceof Error ? error.message : 'Unexpected error' }
  }
  const axiosError = error as AxiosError<{ error?: { code?: string; message?: string; details?: unknown } }>
  if (axiosError.code === 'ECONNABORTED') {
    return { code: 'timeout', message: 'The request timed out. Try a smaller file or retry.' }
  }
  if (axiosError.message === 'Network Error' || !axiosError.response) {
    return {
      code: 'network',
      message: 'Backend unavailable. Start the API on port 8000 or check VITE_API_BASE_URL.',
    }
  }
  const payload = axiosError.response.data?.error
  if (payload?.message) {
    return {
      code: payload.code || String(axiosError.response.status),
      message: payload.message,
      details: payload.details,
    }
  }
  return { code: String(axiosError.response.status), message: 'Request failed. Please try again.' }
}

export async function uploadResume(file: File, onProgress?: (percent: number) => void) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await apiClient.post<ResumeUploadResponse>('/resume/upload', form, {
    onUploadProgress: (event) => {
      if (event.total && onProgress) onProgress(Math.round((event.loaded * 100) / event.total))
    },
  })
  return data
}

export async function analyzeResume(resumeId: string, targetRole: string) {
  const { data } = await apiClient.post<ResumeAnalyzeResponse>('/resume/analyze', {
    resume_id: resumeId,
    target_role: targetRole,
  })
  return data
}

export async function getJobs() {
  const { data } = await apiClient.get<JobListResponse>('/jobs')
  return data
}

export async function searchJobs(params: JobSearchParams) {
  const { data } = await apiClient.get<JobListResponse>('/jobs/search', {
    params: {
      role: params.role || undefined,
      location: params.location || undefined,
      work_mode: params.work_mode || undefined,
      employment_type: params.employment_type || undefined,
      experience_level: params.experience_level || undefined,
      source: params.source || undefined,
      skills: params.skills,
    },
  })
  return data
}

export async function matchJobs(resumeId: string, filters?: JobSearchParams) {
  const { data } = await apiClient.post<JobMatchResponse>('/jobs/match', {
    resume_id: resumeId,
    role: filters?.role || null,
    location: filters?.location || null,
    work_mode: filters?.work_mode || null,
    employment_type: filters?.employment_type || null,
    experience_level: filters?.experience_level || null,
    source: filters?.source || null,
    skills: filters?.skills || [],
  })
  return data
}

export async function getCourseRecommendations(options: {
  skills?: string[]
  resumeId?: string
  targetRole?: string
}) {
  const { data } = await apiClient.get<CourseRecommendResponse>('/courses/recommend', {
    params: {
      skills: options.skills,
      resume_id: options.resumeId,
      target_role: options.targetRole,
    },
  })
  return data
}

export async function getProjectResources(topic: string) {
  const { data } = await apiClient.get<ProjectResourcesResponse>('/projects/resources', {
    params: { topic },
  })
  return data
}

export async function getInterviewQuestions(role: string, difficulty: string) {
  const { data } = await apiClient.get<InterviewQuestionsResponse>('/interview/questions', {
    params: { role, difficulty },
  })
  return data
}

export async function evaluateInterviewAnswer(payload: {
  role: string
  question: string
  answer: string
}) {
  const { data } = await apiClient.post<InterviewEvaluateResponse>('/interview/evaluate', payload)
  return data
}

export async function getJobSources() {
  const { data } = await apiClient.get<{ sources: ProviderStatus[] }>('/jobs/sources')
  return data
}

export async function getHealth() {
  const { data } = await apiClient.get<{ status: string }>('/health')
  return data
}
