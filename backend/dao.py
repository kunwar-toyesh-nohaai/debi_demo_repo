from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Optional
import os

import psycopg2
from psycopg2.extensions import connection as PGConnection
from psycopg2.extras import RealDictCursor


def _load_env_file() -> None:
    """Populate os.environ with values from a project-level .env file if present."""
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / "backend/.env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def _build_connection_kwargs() -> Dict[str, Any]:
    """
    Build connection kwargs for psycopg based on environment variables.

    Precedence:
    1. DATABASE_URL/DB_URL/DB_CONN string
    2. Component-based settings (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, etc.)
    """

    for key in ("DATABASE_URL", "DB_URL", "DB_CONN"):
        conninfo = os.getenv(key)
        if conninfo:
            return {"dsn": conninfo}

    db_name = os.getenv("DB_NAME")
    if not db_name:
        raise RuntimeError(
            "Database name missing. Provide DATABASE_URL or DB_NAME/DB_USER/etc. in the environment."
        )

    kwargs: Dict[str, Any] = {
        "dbname": db_name,
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
    }

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    if user:
        kwargs["user"] = user
    if password:
        kwargs["password"] = password

    sslmode = os.getenv("DB_SSLMODE")
    if sslmode:
        kwargs["sslmode"] = sslmode

    return kwargs


_load_env_file()
CONNECTION_KWARGS = _build_connection_kwargs()


@contextmanager
def get_connection() -> Generator[PGConnection, None, None]:
    connection = psycopg2.connect(**CONNECTION_KWARGS)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _execute_script(connection: PGConnection, statements: Iterable[str]) -> None:
    with connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)


DDL_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS candidates (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(50),
        position_applied VARCHAR(255) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS interviewers (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        department VARCHAR(255),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS interviews (
        id SERIAL PRIMARY KEY,
        candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
        interviewer_id INTEGER NOT NULL REFERENCES interviewers(id) ON DELETE CASCADE,
        scheduled_time TIMESTAMPTZ NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'scheduled',
        location VARCHAR(255),
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        interview_id INTEGER NOT NULL REFERENCES interviews(id) ON DELETE CASCADE,
        rating INTEGER NOT NULL,
        notes TEXT,
        submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """,
)


def init_db() -> None:
    with get_connection() as connection:
        _execute_script(connection, DDL_STATEMENTS)


@dataclass
class CandidateRecord:
    id: int
    full_name: str
    email: str
    position_applied: str
    phone: Optional[str]
    created_at: Any


@dataclass
class InterviewerRecord:
    id: int
    full_name: str
    email: str
    department: Optional[str]
    created_at: Any


@dataclass
class InterviewRecord:
    id: int
    candidate_id: int
    interviewer_id: int
    scheduled_time: Any
    status: str
    location: Optional[str]
    created_at: Any


@dataclass
class FeedbackRecord:
    id: int
    interview_id: int
    rating: int
    notes: Optional[str]
    submitted_at: Any


def _row_to_record(row: Dict[str, Any], record_cls):
    return record_cls(**row)


class InterviewDAO:
    def __init__(self) -> None:
        init_db()

    # Candidate methods
    def list_candidates(self) -> List[Dict[str, Any]]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, full_name, email, phone, position_applied, created_at
                    FROM candidates
                    ORDER BY created_at DESC
                    """
                )
                rows = cursor.fetchall()
                return [asdict(_row_to_record(row, CandidateRecord)) for row in rows]

    def get_candidate(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, full_name, email, phone, position_applied, created_at
                    FROM candidates
                    WHERE id = %s
                    """,
                    (candidate_id,),
                )
                row = cursor.fetchone()
                return asdict(_row_to_record(row, CandidateRecord)) if row else None

    def create_candidate(
        self,
        full_name: str,
        email: str,
        position_applied: str,
        phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO candidates (full_name, email, phone, position_applied)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, full_name, email, phone, position_applied, created_at
                    """,
                    (full_name, email, phone, position_applied),
                )
                row = cursor.fetchone()
                return asdict(_row_to_record(row, CandidateRecord))

    # Interviewer methods
    def list_interviewers(self) -> List[Dict[str, Any]]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, full_name, email, department, created_at
                    FROM interviewers
                    ORDER BY created_at DESC
                    """
                )
                rows = cursor.fetchall()
                return [asdict(_row_to_record(row, InterviewerRecord)) for row in rows]

    def get_interviewer(self, interviewer_id: int) -> Optional[Dict[str, Any]]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, full_name, email, department, created_at
                    FROM interviewers
                    WHERE id = %s
                    """,
                    (interviewer_id,),
                )
                row = cursor.fetchone()
                return asdict(_row_to_record(row, InterviewerRecord)) if row else None

    def create_interviewer(self, full_name: str, email: str, department: Optional[str] = None) -> Dict[str, Any]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO interviewers (full_name, email, department)
                    VALUES (%s, %s, %s)
                    RETURNING id, full_name, email, department, created_at
                    """,
                    (full_name, email, department),
                )
                row = cursor.fetchone()
                return asdict(_row_to_record(row, InterviewerRecord))

    # Interview methods
    def list_interviews(self) -> List[Dict[str, Any]]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, candidate_id, interviewer_id, scheduled_time, status, location, created_at
                    FROM interviews
                    ORDER BY scheduled_time DESC
                    """
                )
                rows = cursor.fetchall()
                return [asdict(_row_to_record(row, InterviewRecord)) for row in rows]

    def create_interview(
        self,
        candidate_id: int,
        interviewer_id: int,
        scheduled_time,
        status: str = "scheduled",
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    INSERT INTO interviews (candidate_id, interviewer_id, scheduled_time, status, location)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, candidate_id, interviewer_id, scheduled_time, status, location, created_at
                    """,
                    (candidate_id, interviewer_id, scheduled_time, status, location),
                )
                row = cursor.fetchone()
                return asdict(_row_to_record(row, InterviewRecord))

    # Feedback methods
    def list_feedback_for_interview(self, interview_id: int) -> List[Dict[str, Any]]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT id, interview_id, rating, notes, submitted_at
                    FROM feedback
                    WHERE interview_id = %s
                    ORDER BY submitted_at DESC
                    """,
                    (interview_id,),
                )
                rows = cursor.fetchall()
                return [asdict(_row_to_record(row, FeedbackRecord)) for row in rows]

    def add_feedback(self, interview_id: int, rating: int, notes: Optional[str] = None) -> Dict[str, Any]:
        with get_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor: # Added cursor_factory here
                cursor.execute(
                    """
                    INSERT INTO feedback (interview_id, rating, notes)
                    VALUES (%s, %s, %s)
                    RETURNING id, interview_id, rating, notes, submitted_at
                    """,
                    (interview_id, rating, notes),
                )
                row = cursor.fetchone()
                return asdict(_row_to_record(row, FeedbackRecord))