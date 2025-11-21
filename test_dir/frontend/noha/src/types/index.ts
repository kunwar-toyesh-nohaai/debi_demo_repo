export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  org_id: string;
  phone?: string;
  profile_photo_url?: string;
  calendly_link?: string;
  is_active: boolean;
  created_at: string;
}

export enum UserRole {
  SUPER_ADMIN = 'SUPER_ADMIN',
  ADMIN = 'ADMIN',
  HIRING_MANAGER = 'HIRING_MANAGER',
  RECRUITER_FULL = 'RECRUITER_FULL',
  RECRUITER_VIEW = 'RECRUITER_VIEW',
  INTERVIEWER = 'INTERVIEWER',
}

export enum InterviewStatus {
  SCHEDULED = 'SCHEDULED',
  ONGOING = 'ONGOING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  NO_SHOW = 'NO_SHOW',
  CANCELLED = 'CANCELLED',
}

export interface Interview {
  id: string;
  org_id: string;
  position_id: string;
  candidate_id: string;
  scheduled_time: string;
  status: InterviewStatus;
  reschedule_count: number;
  meeting_link?: string;
  recording_url?: string;
  transcript_url?: string;
  duration_minutes: number;
  started_at?: string;
  ended_at?: string;
  created_at: string;
  participants: InterviewParticipant[];
}

export interface InterviewParticipant {
  id: string;
  user_id: string;
  joined_at?: string;
  left_at?: string;
}

export interface Candidate {
  id: string;
  org_id: string;
  email: string;
  full_name: string;
  phone?: string;
  resume_url?: string;
  created_at: string;
}

export interface Position {
  id: string;
  org_id: string;
  title: string;
  description?: string;
  status: 'OPEN' | 'CLOSED';
  created_at: string;
  closed_at?: string;
}

export interface Report {
  id: string;
  interview_id: string;
  summary: string;
  strengths?: Record<string, any>;
  weaknesses?: Record<string, any>;
  improvements?: Record<string, any>;
  fit_assessment?: string;
  rating?: number;
  key_moments?: Record<string, any>;
  generated_at: string;
}

export interface DashboardStats {
  total_interviews: number;
  scheduled_interviews: number;
  completed_interviews: number;
  pending_reports: number;
  total_candidates: number;
  total_positions: number;
}
