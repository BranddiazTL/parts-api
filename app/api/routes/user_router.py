from fastapi import APIRouter, Depends
from app.schemas.user_schema import UserResponse
from app.models.user import User
from app.services.security_service import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_logged_in_user(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
