import asyncio
import sys
import os

# Add the current directory to sys.path so we can import app modules
sys.path.append(os.getcwd())

from app.core.security import get_password_hash
from app.core.database import async_session_maker
from app.models.models import User
from sqlalchemy import select

async def reset_admin_password():
    print("--> Connecting to database...")
    async with async_session_maker() as session:
        # Find the admin user
        result = await session.execute(select(User).where(User.email == "admin@noha.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            print("Error: User 'admin@noha.com' not found!")
            return

        print(f"--> Found user: {user.email}")
        
        # Generate new hash
        new_password = "Admin@123"
        new_hash = get_password_hash(new_password)
        print(f"--> Generated new hash for '{new_password}'")
        
        # Update user
        user.password_hash = new_hash
        user.failed_login_attempts = 0  # Reset failed attempts too
        await session.commit()
        
        print("--> Password successfully updated!")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(reset_admin_password())
