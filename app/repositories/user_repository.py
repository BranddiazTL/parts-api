from typing import Optional

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user_schema import UserCreate
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model with CRUD operations."""

    def __init__(self):
        """Initialize with User model."""
        super().__init__(User)

    async def get_by_username(
        self, session: AsyncSession, username: str
    ) -> Optional[User]:
        """Retrieve a user by username."""
        result = await session.execute(
            select(self.model).where(self.model.username == username)
        )
        return result.scalars().first()

    async def get_by_email(
        self, session: AsyncSession, email: EmailStr
    ) -> Optional[User]:
        """Retrieve a user by email."""
        result = await session.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalars().first()

    async def create_user(self, session: AsyncSession, user: UserCreate) -> User:
        """Create a new user from a UserCreate Pydantic schema."""
        user_data = user.model_dump()
        return await self.create(session, user_data)
