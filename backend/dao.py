from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Generator, List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

DATABASE_URL = "sqlite:///./interview_dashboard.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50), nullable=True)
    position_applied = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")


class Interviewer(Base):
    __tablename__ = "interviewers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    department = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    interviews = relationship("Interview", back_populates="interviewer", cascade="all, delete-orphan")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    interviewer_id = Column(Integer, ForeignKey("interviewers.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="scheduled")
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    candidate = relationship("Candidate", back_populates="interviews")
    interviewer = relationship("Interviewer", back_populates="interviews")
    feedback = relationship("Feedback", back_populates="interview", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime, server_default=func.now(), nullable=False)

    interview = relationship("Interview", back_populates="feedback")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class InterviewDAO:
    def __init__(self) -> None:
        init_db()

    # Candidate methods
    def list_candidates(self) -> List[Candidate]:
        with get_session() as session:
            return session.query(Candidate).order_by(Candidate.created_at.desc()).all()

    def get_candidate(self, candidate_id: int) -> Optional[Candidate]:
        with get_session() as session:
            return session.query(Candidate).filter(Candidate.id == candidate_id).first()

    def create_candidate(
        self,
        full_name: str,
        email: str,
        position_applied: str,
        phone: Optional[str] = None,
    ) -> Candidate:
        with get_session() as session:
            candidate = Candidate(
                full_name=full_name,
                email=email,
                phone=phone,
                position_applied=position_applied,
            )
            session.add(candidate)
            session.flush()
            session.refresh(candidate)
            return candidate

    # Interviewer methods
    def list_interviewers(self) -> List[Interviewer]:
        with get_session() as session:
            return session.query(Interviewer).order_by(Interviewer.created_at.desc()).all()

    def create_interviewer(self, full_name: str, email: str, department: Optional[str] = None) -> Interviewer:
        with get_session() as session:
            interviewer = Interviewer(full_name=full_name, email=email, department=department)
            session.add(interviewer)
            session.flush()
            session.refresh(interviewer)
            return interviewer

    # Interview methods
    def list_interviews(self) -> List[Interview]:
        with get_session() as session:
            return (
                session.query(Interview)
                .order_by(Interview.scheduled_time.desc())
                .all()
            )

    def create_interview(
        self,
        candidate_id: int,
        interviewer_id: int,
        scheduled_time: datetime,
        status: str = "scheduled",
        location: Optional[str] = None,
    ) -> Interview:
        with get_session() as session:
            interview = Interview(
                candidate_id=candidate_id,
                interviewer_id=interviewer_id,
                scheduled_time=scheduled_time,
                status=status,
                location=location,
            )
            session.add(interview)
            session.flush()
            session.refresh(interview)
            return interview

    # Feedback methods
    def list_feedback_for_interview(self, interview_id: int) -> List[Feedback]:
        with get_session() as session:
            return (
                session.query(Feedback)
                .filter(Feedback.interview_id == interview_id)
                .order_by(Feedback.submitted_at.desc())
                .all()
            )

    def add_feedback(self, interview_id: int, rating: int, notes: Optional[str] = None) -> Feedback:
        with get_session() as session:
            feedback = Feedback(interview_id=interview_id, rating=rating, notes=notes)
            session.add(feedback)
            session.flush()
            session.refresh(feedback)
            return feedback


