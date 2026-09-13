export interface Job {
  id: number
  title: string
  company: string
  source: string
  url: string | null
  description: string | null
  salary: string | null
  remote: boolean

  location: string | null
  published_at: string | null
  last_seen_at: string | null
  contract_type: string | null
  workday: string | null
  experience: string | null
  education: string | null
  requirements: string | null
  skills: string | null
  keywords: string | null
  is_active: boolean

  created_at: string
}

export interface Match {
  job_id: number
  profile_id: number
  score: number
  skill_score: number
  role_score: number
  salary_score: number
  remote_score: number
  job_skills: string[]
  matched_skills: string[]
  missing_skills: string[]
  recommendation: string
}

export interface Application {
  id: number
  job_id: number
  source: string | null
  application_url: string | null
  applied_at: string | null
  created_at: string
  job?: Job
  match?: Match
}
