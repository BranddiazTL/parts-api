from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.services.security_service import get_password_hash
from app.utils.validation import raise_if_duplicate


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    async def _get_user_or_404(self, session: AsyncSession, user_id: str) -> User:
        """Get a user by ID or raise 404."""
        user = await self.user_repository.get(session, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def _check_user_access(self, user: User, current_user: User) -> None:
        """Check if current_user has access to user, raise 403 if not."""
        if current_user.role != UserRole.ADMIN and str(user.id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )

    async def _check_admin_access(self, current_user: User) -> None:
        """Check if user is admin, raise 403 if not."""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )

    async def create_user(
        self, session: AsyncSession, user_data: UserCreate
    ) -> UserResponse:
        await raise_if_duplicate(
            repo=self.user_repository,
            session=session,
            field_value_pairs=[
                (User.email, user_data.email),
                (User.username, user_data.username),
            ],
        )
        user_dict = user_data.model_dump()
        user_dict["password"] = get_password_hash(user_dict["password"])

        user = await self.user_repository.create(session, user_dict)
        return UserResponse.model_validate(user)

    async def get_user(
        self, session: AsyncSession, user_id: str, current_user: User
    ) -> UserResponse:
        user = await self._get_user_or_404(session, user_id)
        await self._check_user_access(user, current_user)
        return UserResponse.model_validate(user)

    async def update_user(
        self,
        session: AsyncSession,
        user_id: str,
        user_data: UserUpdate,
        current_user: User,
    ) -> UserResponse:
        user = await self._get_user_or_404(session, user_id)
        await self._check_user_access(user, current_user)

        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])

        updated_user = await self.user_repository.update(session, user_id, update_data)
        return UserResponse.model_validate(updated_user)

    async def delete_user(
        self, session: AsyncSession, user_id: str, current_user: User
    ) -> None:
        user = await self._get_user_or_404(session, user_id)
        await self._check_user_access(user, current_user)
        await self.user_repository.delete(session, user_id)

    async def list_users(
        self, session: AsyncSession, current_user: User
    ) -> List[UserResponse]:
        await self._check_admin_access(current_user)
        users = await self.user_repository.list_all(session)
        return [UserResponse.model_validate(user) for user in users]
