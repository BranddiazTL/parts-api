from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.part import Part
from .base_repository import BaseRepository


class PartRepository(BaseRepository[Part]):
    """Repository for Part model with CRUD operations."""

    def __init__(self):
        """Initialize with Part model."""
        super().__init__(Part)

    async def get_by_sku(self, db: AsyncSession, sku: str) -> Optional[Part]:
        """Retrieve a part by its SKU."""
        result = await db.execute(select(self.model).where(self.model.sku == sku))
        return result.scalars().first()
