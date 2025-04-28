import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

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


class PartSortBy(str, Enum):
    visibility = "visibility"
    is_active = "is_active"
    name = "name"
    created_at = "created_at"
    updated_at = "updated_at"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class PartListQueryParams(BaseModel):
    visibility: Optional[PartVisibility] = None
    is_active: Optional[bool] = None
    name: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sort_by: Optional[PartSortBy] = PartSortBy.created_at
    sort_order: Optional[SortOrder] = SortOrder.desc
    limit: Optional[int] = Field(default=20, ge=1, le=100)
    offset: Optional[int] = Field(default=0, ge=0)


class PartPaginatedResponse(BaseModel):
    items: List[PartResponse]
    total: int


class WordFrequencyResponse(BaseModel):
    word: str
    count: int


class TopWordsResponse(BaseModel):
    top_words: list[WordFrequencyResponse]
