"""Session management for REST API chat."""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PendingConfirmation:
    """Represents a pending action that requires user confirmation."""
    request_id: str
    action_type: str  # "write_file" or "commit"
    filepath: Optional[str] = None
    diff: Optional[str] = None
    content: Optional[str] = None
    issue_summary: Optional[str] = None
    commit_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ChatSession:
    """Represents a chat session with the agent."""
    session_id: str
    working_directory: str
    conversation_history: List[ChatMessage] = field(default_factory=list)
    pending_confirmations: Dict[str, PendingConfirmation] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: MessageRole, content: str):
        """Add a message to the conversation history."""
        message = ChatMessage(role=role, content=content)
        self.conversation_history.append(message)
        self.last_activity = datetime.now()
    
    def add_pending_confirmation(self, confirmation: PendingConfirmation):
        """Add a pending confirmation."""
        self.pending_confirmations[confirmation.request_id] = confirmation
        self.last_activity = datetime.now()
    
    def get_pending_confirmation(self, request_id: str) -> Optional[PendingConfirmation]:
        """Get a pending confirmation by ID."""
        return self.pending_confirmations.get(request_id)
    
    def remove_pending_confirmation(self, request_id: str):
        """Remove a pending confirmation."""
        if request_id in self.pending_confirmations:
            del self.pending_confirmations[request_id]
    
    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if session has expired."""
        expiry_time = self.last_activity + timedelta(minutes=timeout_minutes)
        return datetime.now() > expiry_time


class SessionManager:
    """Manages chat sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
    
    def create_session(self, working_directory: str) -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            working_directory=working_directory
        )
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a session by ID."""
        session = self.sessions.get(session_id)
        if session and session.is_expired():
            # Remove expired session
            del self.sessions[session_id]
            return None
        return session
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def cleanup_expired_sessions(self):
        """Remove all expired sessions."""
        expired = [
            sid for sid, session in self.sessions.items()
            if session.is_expired()
        ]
        for sid in expired:
            del self.sessions[sid]
        return len(expired)


# Global session manager instance
session_manager = SessionManager()
