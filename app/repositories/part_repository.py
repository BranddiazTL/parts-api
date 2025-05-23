from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.part import (
    CollaboratorPermission,
    Part,
    PartCollaborator,
    PartVisibility,
)
from app.schemas.part_schema import SortOrder

from .base_repository import BaseRepository


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
            select(self.model).where(self.model.visibility == PartVisibility.PUBLIC)
        )

        return list(result.scalars().all())

    async def list_all(self, session: AsyncSession) -> List[Part]:
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    async def list_filtered(
        self,
        session: AsyncSession,
        params,
        owner_id: Optional[str] = None,
        collaborator_id: Optional[str] = None,
        public_only: bool = False,
    ):
        query = select(self.model)
        filters = []

        if owner_id:
            filters.append(self.model.owner_id == owner_id)
        if collaborator_id:
            query = query.join(
                PartCollaborator, PartCollaborator.part_id == self.model.id
            )
            filters.append(PartCollaborator.user_id == collaborator_id)
        if public_only:
            filters.append(self.model.visibility == PartVisibility.PUBLIC)
        if params.visibility:
            filters.append(self.model.visibility == params.visibility)
        if params.is_active is not None:
            filters.append(self.model.is_active == params.is_active)
        if params.name:
            name_filters = [self.model.name.ilike(f"%{n}%") for n in params.name]
            filters.append(or_(*name_filters))
        if params.start_date:
            filters.append(self.model.created_at >= params.start_date)
        if params.end_date:
            filters.append(self.model.created_at <= params.end_date)

        if filters:
            query = query.where(*filters)

        sort_attr = self.model.created_at
        if params.sort_by:
            sort_attr = getattr(self.model, params.sort_by.value, sort_attr)

        if params.sort_order == SortOrder.desc:
            order_by_clause = sort_attr.desc()
        else:
            order_by_clause = sort_attr.asc()

        query = query.order_by(order_by_clause)
        query = query.offset(params.offset).limit(params.limit)

        result = await session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(self.model)

        if filters:
            count_query = count_query.where(*filters)
        count_result = await session.execute(count_query)
        total = count_result.scalar_one()

        return items, total

    async def get_all_descriptions(self, session: AsyncSession) -> list[str]:
        result = await session.execute(select(self.model.description))
        return [desc for desc in result.scalars().all() if desc]
