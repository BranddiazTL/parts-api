import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base schema for User with common fields."""

    username: Optional[str] = Field(default=None, max_length=50)
    email: EmailStr
    is_active: Optional[bool] = True
    role: Optional[UserRole] = UserRole.MEMBER

    @model_validator(mode="before")
    @classmethod
    def set_username_default(cls, data):
        """Set username to email if not provided."""
        if (
            isinstance(data, dict)
            and data.get("username") is None
            and data.get("email")
        ):
            data["username"] = data["email"]
        return data


class UserCreate(UserBase):
    """Schema for creating a new User."""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating an existing User."""

    username: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    """Schema for returning a User, including id and timestamps."""

    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
