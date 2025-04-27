from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.user_schema import UserUpdate, UserResponse
from app.services.user_service import UserService
from app.api.dependencies import get_db_session
from app.services.security_service import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

user_service = UserService()


@router.get("/me", response_model=UserResponse)
async def get_logged_in_user(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("", response_model=List[UserResponse])
async def list_users(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> List[UserResponse]:
    return await user_service.list_users(session, current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    return await user_service.get_user(session, user_id, current_user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user: UserUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    return await user_service.update_user(session, user_id, user, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    await user_service.delete_user(session, user_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
