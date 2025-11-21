from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import decode_token
from app.models.models import User, UserRole

security = HTTPBearer()


class CurrentUser:
    """Dependency to get the current authenticated user."""
    
    def __init__(self, required_roles: Optional[list[UserRole]] = None):
        self.required_roles = required_roles or []
    
    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        token = credentials.credentials
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user ID from token
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Fetch user from database
        result = await db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Check if user is locked
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is locked"
            )
        
        # Check role permissions
        if self.required_roles and user.role not in self.required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return user


# Common dependency instances
get_current_user = CurrentUser()
get_super_admin = CurrentUser(required_roles=[UserRole.SUPER_ADMIN])
get_admin_or_super = CurrentUser(required_roles=[UserRole.SUPER_ADMIN, UserRole.ADMIN])
get_recruiter_full = CurrentUser(required_roles=[
    UserRole.SUPER_ADMIN,
    UserRole.ADMIN,
    UserRole.RECRUITER_FULL
])


def check_org_access(user: User, org_id: UUID) -> bool:
    """Check if user has access to the organization."""
    if user.role == UserRole.SUPER_ADMIN:
        return True
    return user.org_id == org_id
