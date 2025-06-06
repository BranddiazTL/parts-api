from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    oauth2_scheme,
    pwd_context,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.security_schema import TokenData

user_repository = UserRepository()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Access token created for user: {data.get('sub', 'unknown')}")
    return encoded_jwt


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> Optional[User]:
    user = await user_repository.get_by_username(session, username)
    if not user:
        user = await user_repository.get_by_email(session, email=username)

    if not user or not verify_password(password, user.password):
        logger.warning(f"Authentication failed for user: {username}")
        return None

    logger.info(f"Authentication successful for user: {username}")
    return user


async def get_current_user(
    session: AsyncSession = Depends(get_db_session), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            logger.warning("JWT payload missing 'sub' field.")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        logger.warning("JWT decoding failed.")
        raise credentials_exception

    if token_data.username is None:
        logger.warning("Token data missing username.")
        raise credentials_exception

    user = await user_repository.get_by_username(session, username=token_data.username)
    if not user:
        user = await user_repository.get_by_email(session, email=token_data.username)

    if user is None:
        logger.warning(f"User not found for token username: {token_data.username}")
        raise credentials_exception

    logger.info(f"Current user validated: {user.username}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        logger.warning(f"Inactive user trying to get in: {current_user.username}")
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user
