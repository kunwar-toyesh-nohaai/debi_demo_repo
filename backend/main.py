from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from backend.dao import InterviewDAO

app = FastAPI(title="Interview Dashboard API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # accept requests from any origin
    allow_credentials=True,
    allow_methods=["*"],          # permit all HTTP methods
    allow_headers=["*"],          # permit all request headers
)
dao = InterviewDAO()


class CandidateCreate(BaseModel):
    full_name: str = Field(..., max_length=255)
    email: EmailStr
    position_applied: str = Field(..., max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)


class CandidateRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    position_applied: str
    phone: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class InterviewerCreate(BaseModel):
    full_name: str = Field(..., max_length=255)
    email: EmailStr
    department: Optional[str] = Field(default=None, max_length=255)


class InterviewerRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    department: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class InterviewCreate(BaseModel):
    candidate_id: int
    interviewer_id: int
    scheduled_time: datetime
    status: Optional[str] = Field(default="scheduled", max_length=50)
    location: Optional[str] = Field(default=None, max_length=255)


class InterviewRead(BaseModel):
    id: int
    candidate_id: int
    interviewer_id: int
    scheduled_time: datetime
    status: str
    location: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class FeedbackCreate(BaseModel):
    interview_id: int
    rating: int = Field(..., ge=1, le=5)
    notes: Optional[str] = None


class FeedbackRead(BaseModel):
    id: int
    interview_id: int
    rating: int
    notes: Optional[str]
    submitted_at: datetime

    class Config:
        orm_mode = True


def get_dao() -> InterviewDAO:
    return dao


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/candidates", response_model=List[CandidateRead])
def list_candidates(dao: InterviewDAO = Depends(get_dao)) -> List[CandidateRead]:
    return dao.list_candidates()


@app.post("/candidates", response_model=CandidateRead, status_code=201)
def create_candidate(payload: CandidateCreate, dao: InterviewDAO = Depends(get_dao)) -> CandidateRead:
    return dao.create_candidate(
        full_name=payload.full_name,
        email=payload.email,
        position_applied=payload.position_applied,
        phone=payload.phone,
    )


@app.get("/interviewers", response_model=List[InterviewerRead])
def list_interviewers(dao: InterviewDAO = Depends(get_dao)) -> List[InterviewerRead]:
    return dao.list_interviewers()


@app.post("/interviewers", response_model=InterviewerRead, status_code=201)
def create_interviewer(payload: InterviewerCreate, dao: InterviewDAO = Depends(get_dao)) -> InterviewerRead:
    return dao.create_interviewer(
        full_name=payload.full_name,
        email=payload.email,
        department=payload.department,
    )


@app.get("/interviews", response_model=List[InterviewRead])
def list_interviews(dao: InterviewDAO = Depends(get_dao)) -> List[InterviewRead]:
    return dao.list_interviews()


@app.post("/interviews", response_model=InterviewRead, status_code=201)
def create_interview(payload: InterviewCreate, dao: InterviewDAO = Depends(get_dao)) -> InterviewRead:
    # Validate candidate and interviewer exist before creating interview
    if not dao.get_candidate(payload.candidate_id):
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not dao.get_interviewer(payload.interviewer_id):
        raise HTTPException(status_code=404, detail="Interviewer not found")
    return dao.create_interview(
        candidate_id=payload.candidate_id,
        interviewer_id=payload.interviewer_id,
        scheduled_time=payload.scheduled_time,
        status=payload.status or "scheduled",
        location=payload.location,
    )


@app.post("/interviews/schedule", response_model=InterviewRead, status_code=201)
def schedule_interview(payload: InterviewCreate, dao: InterviewDAO = Depends(get_dao)) -> InterviewRead:
    return create_interview(payload, dao)


@app.get("/interviews/{interview_id}/feedback", response_model=List[FeedbackRead])
def list_feedback(interview_id: int, dao: InterviewDAO = Depends(get_dao)) -> List[FeedbackRead]:
    return dao.list_feedback_for_interview(interview_id)


@app.post("/feedback", response_model=FeedbackRead, status_code=201)
def add_feedback(payload: FeedbackCreate, dao: InterviewDAO = Depends(get_dao)) -> FeedbackRead:
    try:
        return dao.add_feedback(
            interview_id=payload.interview_id,
            rating=payload.rating,
            notes=payload.notes,
        )
    except Exception as exc:  # pragma: no cover - basic demo handling
        raise HTTPException(status_code=400, detail=str(exc)) from exc