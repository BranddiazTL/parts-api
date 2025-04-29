import re
from collections import Counter
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.part import CollaboratorPermission, Part, PartVisibility
from app.models.user import User, UserRole
from app.repositories.part_repository import PartRepository
from app.repositories.user_repository import UserRepository
from app.schemas.part_schema import (
    PartCollaboratorResponse,
    PartCreate,
    PartListQueryParams,
    PartPaginatedResponse,
    PartResponse,
    PartUpdate,
    PartUpdateForCollaborators,
    TopWordsResponse,
    WordFrequencyResponse,
)
from app.utils.validation import raise_if_duplicate


class PartService:
    def __init__(self) -> None:
        self.part_repository = PartRepository()
        self.user_repository = UserRepository()

    async def _get_part_or_404(
        self, session: AsyncSession, part_id: str
    ) -> PartResponse:
        """Get a part by ID or raise 404."""
        part = await self.part_repository.get(session, part_id)
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Part not found"
            )

        return PartResponse.model_validate(part)

    async def _check_part_access(
        self, session: AsyncSession, part: PartResponse, user: Optional[User]
    ) -> None:
        """Check if user has access to part, raise 403 if not."""
        if part.visibility == PartVisibility.PUBLIC:
            return
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )
        if user.role == UserRole.ADMIN or str(part.owner_id) == str(user.id):
            return
        collaborator = await self.part_repository.get_collaborator(
            session, str(part.id), str(user.id)
        )
        if not collaborator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )

    async def _check_part_edit_access(
        self, session: AsyncSession, part: PartResponse, user: User
    ) -> None:
        """Check if user has edit access to part, raise 403 if not."""
        if user.role == UserRole.ADMIN or str(part.owner_id) == str(user.id):
            return
        collaborator = await self.part_repository.get_collaborator(
            session, str(part.id), str(user.id)
        )
        if not collaborator or collaborator.permission != CollaboratorPermission.EDIT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )

    async def _check_part_owner_access(self, part: PartResponse, user: User) -> None:
        """Check if user is owner or admin, raise 403 if not."""
        if user.role != UserRole.ADMIN and str(part.owner_id) != str(user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
            )

    async def create_part(
        self, session: AsyncSession, part_data: PartCreate, owner: User
    ) -> PartResponse:
        await raise_if_duplicate(
            repo=self.part_repository,
            session=session,
            field_value_pairs=[
                (Part.sku, part_data.sku),
            ],
        )
        part_dict = part_data.model_dump()
        part_dict["owner_id"] = str(owner.id)
        part = await self.part_repository.create(session, part_dict)

        return PartResponse.model_validate(part)

    async def get_part(
        self, session: AsyncSession, part_id: str, user: Optional[User]
    ) -> PartResponse:
        part = await self._get_part_or_404(session, part_id)
        await self._check_part_access(session, part, user)

        return PartResponse.model_validate(part)

    async def update_part(
        self, session: AsyncSession, part_id: str, part_data: PartUpdate, user: User
    ) -> PartResponse:
        part = await self._get_part_or_404(session, part_id)
        await self._check_part_edit_access(session, part, user)

        is_owner_or_admin = user.role == UserRole.ADMIN or str(part.owner_id) == str(
            user.id
        )
        if is_owner_or_admin:
            update_fields = part_data.model_dump(exclude_unset=True)
        else:
            update_data = part_data.model_dump(exclude_unset=True)
            allowed_fields = set(PartUpdateForCollaborators.model_fields)
            excluded_fields = [f for f in update_data if f not in allowed_fields]
            if excluded_fields:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not authorized to update: {', '.join(excluded_fields)}",
                )
            collaborator_update = PartUpdateForCollaborators.model_validate(update_data)
            update_fields = collaborator_update.model_dump(exclude_unset=True)

        updated = await self.part_repository.update(session, part_id, update_fields)

        return PartResponse.model_validate(updated)

    async def delete_part(
        self, session: AsyncSession, part_id: str, user: User
    ) -> None:
        part = await self._get_part_or_404(session, part_id)
        await self._check_part_owner_access(part, user)

        await self.part_repository.delete(session, part_id)

    async def list_parts(
        self, session: AsyncSession, user: Optional[User], params: PartListQueryParams
    ) -> PartPaginatedResponse:
        if user and user.role == UserRole.ADMIN:
            items, total = await self.part_repository.list_filtered(session, params)
            return PartPaginatedResponse(
                items=[PartResponse.model_validate(p) for p in items], total=total
            )

        if user:
            owned, owned_total = await self.part_repository.list_filtered(
                session, params, owner_id=str(user.id)
            )
            collab, collab_total = await self.part_repository.list_filtered(
                session, params, collaborator_id=str(user.id)
            )
            public, public_total = await self.part_repository.list_filtered(
                session, params, public_only=True
            )
            parts = {p.id: p for p in (owned + collab + public)}
            return PartPaginatedResponse(
                items=[PartResponse.model_validate(p) for p in parts.values()],
                total=len(parts),
            )

        items, total = await self.part_repository.list_filtered(
            session, params, public_only=True
        )
        return PartPaginatedResponse(
            items=[PartResponse.model_validate(p) for p in items], total=total
        )

    async def add_collaborator(
        self,
        session: AsyncSession,
        part_id: str,
        user_id: str,
        permission: CollaboratorPermission,
        owner: User,
    ) -> PartCollaboratorResponse:
        part = await self._get_part_or_404(session, part_id)

        await self._check_part_owner_access(part, owner)
        collaborator = await self.part_repository.add_collaborator(
            session, part_id, user_id, permission
        )

        return PartCollaboratorResponse.model_validate(collaborator)

    async def remove_collaborator(
        self, session: AsyncSession, part_id: str, user_id: str, owner: User
    ) -> None:
        part = await self._get_part_or_404(session, part_id)
        await self._check_part_owner_access(part, owner)

        await self.part_repository.remove_collaborator(session, part_id, user_id)

    async def get_top_words_in_descriptions(
        self, session: AsyncSession, top_number_of_words: int = 5
    ) -> TopWordsResponse:
        descriptions = await self.part_repository.get_all_descriptions(session)

        words = []
        for desc in descriptions:
            words += re.findall(r"\b\w+\b", desc.lower())
        counter = Counter(words)

        # here the magic happens with heaps under the most_common method
        most_common = counter.most_common(top_number_of_words)

        return TopWordsResponse(
            top_words=[WordFrequencyResponse(word=w, count=c) for w, c in most_common]
        )
