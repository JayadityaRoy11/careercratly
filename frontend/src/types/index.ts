export interface ResumeUploadResponse {
  resume_id: string
  filename: string
  file_type: string
  text: string
  pages: number
  metadata: Record<string, unknown>
  extracted_skills: string[]
}

export interface PartialMatch {
  skill: string
  related_found: string
  note: string
}

export interface ScoreComponents {
  required_skill_coverage: number
  preferred_skill_coverage: number
  keyword_relevance: number
  experience_project_relevance: number
  resume_section_completeness: number
}

export interface ResumeAnalyzeResponse {
  resume_id: string
  score: number
  score_label: string
  target_role: string
  target_role_slug: string
  matched_skills: string[]
  missing_skills: string[]
  partial_matches: PartialMatch[]
  strengths: string[]
  improvements: string[]
  recommended_keywords: string[]
  recommended_certifications: string[]
  recommended_project_themes: string[]
  components: ScoreComponents
  disclaimer: string
  extracted_skills: string[]
  intelligence?: ResumeIntelligence
}

export interface ResumeIntelligence {
  overview: {
    what_is_good: string
    why_it_is_good: string
    what_is_missing: string
    why_it_matters: string
    what_to_change: string
    how_to_change: string
    skills_to_learn: string[]
    project_ideas: string[]
    certifications: string[]
  }
  keyword_gap: {
    detected: string[]
    missing: string[]
    weak: string[]
    placement: { skill: string; advice: string }[]
  }
  section_reviews: {
    name: string
    status: string
    score: number
    strengths: string[]
    issues: string[]
    improvements: string[]
  }[]
  bullet_analysis: {
    guidance: string
    items: { text: string; problem: string; suggested_structure: string }[]
    weak_count: number
  }
  projects_analysis: {
    title: string
    detected_skills: string[]
    missing_information: string[]
    recommendations: string[]
  }[]
  alignment: Record<string, { score: number; explanation: string }>
  roadmap: {
    high: { issue: string; why: string; what: string; benefit: string }[]
    medium: { issue: string; why: string; what: string; benefit: string }[]
    optional: { issue: string; why: string; what: string; benefit: string }[]
  }
  metric_policy: string
}

export interface JobListing {
  id: string
  title: string
  company: string
  location: string
  work_mode: 'remote' | 'hybrid' | 'onsite'
  employment_type: 'internship' | 'full_time' | 'part_time'
  skills: string[]
  description: string
  source: string
  source_logo?: string
  external_url: string
  posted_date: string
  is_demo?: boolean
}

export interface MatchedJob extends JobListing {
  match_score: number
  matched_skills: string[]
  missing_skills: string[]
}

export interface JobListResponse {
  items: JobListing[]
  count: number
  sources?: ProviderStatus[]
}

export interface JobMatchResponse {
  resume_id: string
  items: MatchedJob[]
  count: number
  sources?: ProviderStatus[]
}

export interface ProviderStatus {
  provider: string
  status: string
  message: string
  live: boolean
}

export interface CoursePublic {
  id: string
  title: string
  provider: string
  skill_tag: string
  level: string | null
  url: string
  placeholder: boolean
}

export interface CourseRecommendResponse {
  recommendations: { skill: string; courses: CoursePublic[] }[]
}

export interface ProjectResource {
  title: string
  type: string
  source: string
  url: string
}

export interface ProjectResourcesResponse {
  topic: string
  resources: ProjectResource[]
}

export interface InterviewQuestion {
  id: string
  question: string
}

export interface InterviewQuestionsResponse {
  role: string
  difficulty: string
  questions: InterviewQuestion[]
}

export interface InterviewEvaluateResponse {
  score: number
  keyword_coverage: number
  technical_relevance: number
  structure_score: number
  strengths: string[]
  missing_keywords: string[]
  suggestions: string[]
}

export interface JobSearchParams {
  role?: string
  location?: string
  work_mode?: string
  employment_type?: string
  skills?: string[]
  source?: string
  experience_level?: string
}
