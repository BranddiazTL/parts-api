from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.part import Part, CollaboratorPermission
from .base_repository import BaseRepository
from app.models.part import PartCollaborator


class PartRepository(BaseRepository[Part]):
    """Repository for Part model with CRUD operations."""

    def __init__(self):
        """Initialize with Part model."""
        super().__init__(Part)

    async def get_by_sku(self, session: AsyncSession, sku: str) -> Optional[Part]:
        """Retrieve a part by its SKU."""
        result = await session.execute(select(self.model).where(self.model.sku == sku))

        return result.scalars().first()

    async def get_collaborator(
        self, session: AsyncSession, part_id: str, user_id: str
    ) -> Optional[PartCollaborator]:
        result = await session.execute(
            select(PartCollaborator).where(
                PartCollaborator.part_id == part_id,
                PartCollaborator.user_id == user_id,
            )
        )

        return result.scalars().first()

    async def add_collaborator(
        self,
        session: AsyncSession,
        part_id: str,
        user_id: str,
        permission: CollaboratorPermission,
    ) -> PartCollaborator:
        collaborator = PartCollaborator(
            part_id=part_id, user_id=user_id, permission=permission
        )
        session.add(collaborator)
        await session.commit()

        return collaborator

    async def remove_collaborator(
        self, session: AsyncSession, part_id: str, user_id: str
    ) -> Optional[PartCollaborator]:
        result = await session.execute(
            select(PartCollaborator).where(
                PartCollaborator.part_id == part_id,
                PartCollaborator.user_id == user_id,
            )
        )
        collaborator = result.scalars().first()
        if collaborator:
            await session.delete(collaborator)
            await session.commit()

        return collaborator

    async def list_by_owner(self, session: AsyncSession, owner_id: str) -> List[Part]:
        result = await session.execute(
            select(self.model).where(self.model.owner_id == owner_id)
        )

        return list(result.scalars().all())

    async def list_by_collaborator(
        self, session: AsyncSession, user_id: str
    ) -> List[Part]:
        result = await session.execute(
            select(self.model)
            .join(PartCollaborator, PartCollaborator.part_id == self.model.id)
            .where(PartCollaborator.user_id == user_id)
        )

        return list(result.scalars().all())

    async def list_public(self, session: AsyncSession) -> List[Part]:
        result = await session.execute(
            select(self.model).where(self.model.visibility == "PUBLIC")
        )

        return list(result.scalars().all())

    async def list_all(self, session: AsyncSession) -> List[Part]:
        result = await session.execute(select(self.model))
        return list(result.scalars().all())
