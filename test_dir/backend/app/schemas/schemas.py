from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.models import UserRole, PositionStatus, InterviewStatus


# ========== Auth Schemas ==========
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


# ========== User Schemas ==========
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    phone: Optional[str] = None
    calendly_link: Optional[str] = None


class UserCreate(UserBase):
    password: str
    org_id: UUID


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    profile_photo_url: Optional[str] = None
    calendly_link: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    org_id: UUID
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== Organization Schemas ==========
class OrganizationBase(BaseModel):
    name: str
    domain: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== Position Schemas ==========
class PositionBase(BaseModel):
    title: str
    description: Optional[str] = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PositionStatus] = None


class PositionResponse(PositionBase):
    id: UUID
    org_id: UUID
    status: PositionStatus
    created_at: datetime
    closed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ========== Candidate Schemas ==========
class CandidateBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


class CandidateCreate(CandidateBase):
    resume_url: Optional[str] = None


class CandidateResponse(CandidateBase):
    id: UUID
    org_id: UUID
    resume_url: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== Interview Schemas ==========
class InterviewBase(BaseModel):
    scheduled_time: datetime
    position_id: UUID
    candidate_id: UUID


class InterviewCreate(InterviewBase):
    interviewer_ids: List[UUID] = Field(default_factory=list)
    calendly_event_id: Optional[str] = None


class InterviewUpdate(BaseModel):
    scheduled_time: Optional[datetime] = None
    status: Optional[InterviewStatus] = None


class InterviewReschedule(BaseModel):
    new_scheduled_time: datetime
    reason: Optional[str] = None


class InterviewParticipantResponse(BaseModel):
    id: UUID
    user_id: UUID
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class InterviewResponse(InterviewBase):
    id: UUID
    org_id: UUID
    status: InterviewStatus
    reschedule_count: int
    meeting_link: Optional[str] = None
    recording_url: Optional[str] = None
    transcript_url: Optional[str] = None
    duration_minutes: int
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    participants: List[InterviewParticipantResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# ========== Report Schemas ==========
class ReportResponse(BaseModel):
    id: UUID
    interview_id: UUID
    summary: str
    strengths: Optional[dict] = None
    weaknesses: Optional[dict] = None
    improvements: Optional[dict] = None
    fit_assessment: Optional[str] = None
    rating: Optional[int] = None
    key_moments: Optional[dict] = None
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ========== Dashboard Schemas ==========
class DashboardStatsResponse(BaseModel):
    total_interviews: int
    scheduled_interviews: int
    completed_interviews: int
    pending_reports: int
    total_candidates: int
    total_positions: int
