from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models.models import Interview, User, InterviewParticipant, InterviewStatus, Candidate
from app.schemas.schemas import (
    InterviewCreate, InterviewResponse, InterviewUpdate,
    InterviewReschedule, DashboardStatsResponse
)
from app.api.deps import get_current_user, get_recruiter_full, check_org_access

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def create_interview(
    interview_data: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_recruiter_full)
):
    """Create a new interview."""
    # Create interview
    new_interview = Interview(
        org_id=current_user.org_id,
        position_id=interview_data.position_id,
        candidate_id=interview_data.candidate_id,
        scheduled_time=interview_data.scheduled_time,
        calendly_event_id=interview_data.calendly_event_id,
        created_by=current_user.id,
        meeting_link=f"/interview/{str(__import__('uuid').uuid4())}"  # Generate unique link
    )
    
    db.add(new_interview)
    await db.flush()
    
    # Add participants
    for interviewer_id in interview_data.interviewer_ids:
        participant = InterviewParticipant(
            interview_id=new_interview.id,
            user_id=interviewer_id
        )
        db.add(participant)
    
    await db.commit()
    await db.refresh(new_interview)
    
    # Load participants
    result = await db.execute(
        select(Interview)
        .options(selectinload(Interview.participants))
        .where(Interview.id == new_interview.id)
    )
    interview_with_participants = result.scalar_one()
    
    return interview_with_participants


@router.get("", response_model=List[InterviewResponse])
async def list_interviews(
    status_filter: Optional[InterviewStatus] = Query(None),
    position_id: Optional[UUID] = Query(None),
    candidate_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all interviews with optional filters."""
    query = select(Interview).options(selectinload(Interview.participants))
    
    # Filter by organization
    query = query.where(Interview.org_id == current_user.org_id)
    
    # Apply filters
    if status_filter:
        query = query.where(Interview.status == status_filter)
    if position_id:
        query = query.where(Interview.position_id == position_id)
    if candidate_id:
        query = query.where(Interview.candidate_id == candidate_id)
    
    # Order by scheduled time
    query = query.order_by(Interview.scheduled_time.desc())
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    interviews = result.scalars().all()
    
    return interviews


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get interview by ID."""
    result = await db.execute(
        select(Interview)
        .options(selectinload(Interview.participants))
        .where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Check organization access
    if not check_org_access(current_user, interview.org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return interview


@router.patch("/{interview_id}/reschedule", response_model=InterviewResponse)
async def reschedule_interview(
    interview_id: UUID,
    reschedule_data: InterviewReschedule,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_recruiter_full)
):
    """Reschedule an interview."""
    result = await db.execute(
        select(Interview).where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Check organization access
    if not check_org_access(current_user, interview.org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check reschedule limit
    if interview.reschedule_count >= 2:
        interview.status = InterviewStatus.CANCELLED
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum reschedule limit reached. Interview has been cancelled."
        )
    
    # Update interview
    interview.scheduled_time = reschedule_data.new_scheduled_time
    interview.reschedule_count += 1
    
    await db.commit()
    await db.refresh(interview)
    
    return interview


@router.post("/{interview_id}/cancel")
async def cancel_interview(
    interview_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_recruiter_full)
):
    """Cancel an interview."""
    result = await db.execute(
        select(Interview).where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Check organization access
    if not check_org_access(current_user, interview.org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    interview.status = InterviewStatus.CANCELLED
    await db.commit()
    
    return {"message": "Interview cancelled successfully"}


@router.post("/{interview_id}/start")
async def start_interview(
    interview_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start an interview."""
    result = await db.execute(
        select(Interview).where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Check organization access
    if not check_org_access(current_user, interview.org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    interview.status = InterviewStatus.ONGOING
    interview.started_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Interview started", "meeting_link": interview.meeting_link}


@router.post("/{interview_id}/end")
async def end_interview(
    interview_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """End an interview."""
    result = await db.execute(
        select(Interview).where(Interview.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Check organization access
    if not check_org_access(current_user, interview.org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    interview.status = InterviewStatus.COMPLETED
    interview.ended_at = datetime.utcnow()
    await db.commit()
    
    # TODO: Trigger async task to generate report
    
    return {"message": "Interview ended successfully"}


@router.get("/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics."""
    org_id = current_user.org_id
    
    # Total interviews
    total_result = await db.execute(
        select(func.count(Interview.id)).where(Interview.org_id == org_id)
    )
    total_interviews = total_result.scalar()
    
    # Scheduled interviews
    scheduled_result = await db.execute(
        select(func.count(Interview.id)).where(
            Interview.org_id == org_id,
            Interview.status == InterviewStatus.SCHEDULED
        )
    )
    scheduled_interviews = scheduled_result.scalar()
    
    # Completed interviews
    completed_result = await db.execute(
        select(func.count(Interview.id)).where(
            Interview.org_id == org_id,
            Interview.status == InterviewStatus.COMPLETED
        )
    )
    completed_interviews = completed_result.scalar()
    
    # Pending reports (completed interviews without reports)
    from app.models.models import Report
    pending_reports_result = await db.execute(
        select(func.count(Interview.id))
        .outerjoin(Report, Interview.id == Report.interview_id)
        .where(
            Interview.org_id == org_id,
            Interview.status == InterviewStatus.COMPLETED,
            Report.id.is_(None)
        )
    )
    pending_reports = pending_reports_result.scalar()
    
    # Total candidates
    candidates_result = await db.execute(
        select(func.count(Candidate.id)).where(Candidate.org_id == org_id)
    )
    total_candidates = candidates_result.scalar()
    
    # Total positions
    from app.models.models import Position
    positions_result = await db.execute(
        select(func.count(Position.id)).where(Position.org_id == org_id)
    )
    total_positions = positions_result.scalar()
    
    return DashboardStatsResponse(
        total_interviews=total_interviews,
        scheduled_interviews=scheduled_interviews,
        completed_interviews=completed_interviews,
        pending_reports=pending_reports,
        total_candidates=total_candidates,
        total_positions=total_positions
    )
