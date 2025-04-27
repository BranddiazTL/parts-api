from pydantic import BaseModel, field_validator
from typing import Optional
import uuid
from datetime import datetime
from app.models.part import PartVisibility


class PartFieldValidatorMixin:
    @field_validator("visibility", mode="before")
    @classmethod
    def validate_visibility(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v


class PartBase(PartFieldValidatorMixin, BaseModel):
    """Base schema for Part with common fields."""

    name: str
    sku: str
    description: Optional[str] = None
    weight_ounces: Optional[int] = None
    is_active: Optional[bool] = True
    visibility: PartVisibility = PartVisibility.PUBLIC


class PartCreate(PartBase):
    """Schema for creating a new Part."""

    pass


class PartUpdate(PartFieldValidatorMixin, BaseModel):
    """Schema for updating an existing Part."""

    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    weight_ounces: Optional[int] = None
    is_active: Optional[bool] = None
    visibility: Optional[PartVisibility] = None


class PartResponse(PartBase):
    """Schema for returning a Part, including id and timestamps."""

    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    visibility: PartVisibility
    owner_id: uuid.UUID

    model_config = {"from_attributes": True}


class PartCollaboratorResponse(BaseModel):
    """Schema for returning a Part Collaborator."""

    part_id: str
    user_id: str
    permission: str

    model_config = {"from_attributes": True}


class PartUpdateForCollaborators(BaseModel):
    """Schema for updating a Part by collaborators (excluding is_active and visibility fields)."""

    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    weight_ounces: Optional[int] = None
