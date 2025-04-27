from pydantic import BaseModel, field_validator
from typing import Optional
import uuid


class UserBase(BaseModel):
    """Base schema for User with common fields."""

    username: Optional[str] = None
    email: str
    is_active: Optional[bool] = True

    @field_validator("username", mode="before")
    def set_username_default(cls, v, info):
        """Set username to email if not provided."""
        if v is not None:
            return v
        return info.data.get("email")


class UserCreate(UserBase):
    """Schema for creating a new User."""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating an existing User."""

    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for returning a User, including id and timestamps."""

    id: uuid.UUID
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True
