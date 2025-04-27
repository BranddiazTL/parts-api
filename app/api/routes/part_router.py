from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.part_schema import (
    PartCreate,
    PartUpdate,
    PartResponse,
    PartCollaboratorResponse,
)
from app.models.part import CollaboratorPermission
from app.services.part_service import PartService
from app.api.dependencies import get_db_session
from app.services.security_service import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/parts", tags=["parts"])

part_service = PartService()


@router.post("", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
async def create_part(
    part: PartCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> PartResponse:
    return await part_service.create_part(session, part, current_user)


@router.get("", response_model=List[PartResponse])
async def list_parts(
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_active_user),
) -> List[PartResponse]:
    return await part_service.list_parts(session, current_user)


@router.get("/{part_id}", response_model=PartResponse)
async def get_part(
    part_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_active_user),
) -> PartResponse:
    return await part_service.get_part(session, part_id, current_user)


@router.patch("/{part_id}", response_model=PartResponse)
async def update_part(
    part_id: str,
    part: PartUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> PartResponse:
    return await part_service.update_part(session, part_id, part, current_user)


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(
    part_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    await part_service.delete_part(session, part_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{part_id}/collaborators/{user_id}",
    response_model=PartCollaboratorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_collaborator(
    part_id: str,
    user_id: str,
    permission: CollaboratorPermission,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> PartCollaboratorResponse:
    return await part_service.add_collaborator(
        session, part_id, user_id, permission, current_user
    )


@router.delete(
    "/{part_id}/collaborators/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_collaborator(
    part_id: str,
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    await part_service.remove_collaborator(session, part_id, user_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
