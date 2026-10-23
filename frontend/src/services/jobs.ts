import { getJobs, getJobSources, matchJobs, searchJobs } from '@/lib/api'

export { getJobs, getJobSources, matchJobs, searchJobs }

export async function getJob(jobId: string) {
  const data = await getJobs()
  return data.items.find((job) => job.id === jobId) || null
}

export async function matchJobsToResume(
  resumeId: string,
  filters?: Parameters<typeof matchJobs>[1],
) {
  return matchJobs(resumeId, filters)
}
