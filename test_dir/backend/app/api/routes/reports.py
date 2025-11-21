from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.models.models import Report, Interview, User
from app.schemas.schemas import ReportResponse
from app.api.deps import get_current_user, check_org_access

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{interview_id}", response_model=ReportResponse)
async def get_report(
    interview_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get report for an interview."""
    # Get interview first to check access
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
    
    # Get report
    result = await db.execute(
        select(Report).where(Report.interview_id == interview_id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found. It may still be generating."
        )
    
    return report


@router.post("/{interview_id}/regenerate", response_model=ReportResponse)
async def regenerate_report(
    interview_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Regenerate report for an interview."""
    # Get interview first to check access
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
    
    # Check if interview has transcript
    if not interview.transcript_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transcript available for this interview"
        )
    
    # Get existing report
    result = await db.execute(
        select(Report).where(Report.interview_id == interview_id)
    )
    report = result.scalar_one_or_none()
    
    if report:
        # Increment regenerated count
        report.regenerated_count += 1
        await db.commit()
    
    # TODO: Trigger async task to regenerate report using OpenAI
    # For now, return existing report or placeholder
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report to regenerate"
        )
    
    return report
