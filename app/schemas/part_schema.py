from pydantic import BaseModel
from typing import Optional
import uuid


class PartBase(BaseModel):
    """Base schema for Part with common fields."""

    name: str
    sku: str
    description: Optional[str] = None
    weight_ounces: Optional[int] = None
    is_active: Optional[bool] = True


class PartCreate(PartBase):
    """Schema for creating a new Part."""

    pass


class PartUpdate(BaseModel):
    """Schema for updating an existing Part."""

    name: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None
    weight_ounces: Optional[int] = None
    is_active: Optional[bool] = None


class PartResponse(PartBase):
    """Schema for returning a Part, including id and timestamps."""

    id: uuid.UUID
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}
