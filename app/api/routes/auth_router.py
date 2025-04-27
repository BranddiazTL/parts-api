from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.security_schema import Token, TokenType
from app.schemas.user_schema import UserResponse, UserCreate
from app.services.security_service import (
    authenticate_user,
    create_access_token,
)
from app.services.user_service import UserService
from datetime import timedelta
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES
from app.api.dependencies import get_db_session

router = APIRouter(prefix="/auth", tags=["auth"])
user_service = UserService()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type=TokenType.BEARER)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
    user_create: UserCreate, session: AsyncSession = Depends(get_db_session)
) -> UserResponse:
    user = await user_service.create_user(session, user_create)

    return UserResponse.model_validate(user)
