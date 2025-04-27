from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model with CRUD operations."""

    def __init__(self):
        """Initialize with User model."""
        super().__init__(User)

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Retrieve a user by username."""
        result = await db.execute(
            select(self.model).where(self.model.username == username)
        )
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Retrieve a user by email."""
        result = await db.execute(select(self.model).where(self.model.email == email))
        return result.scalars().first()
