from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session
from app.models.part import CollaboratorPermission, PartVisibility
from app.models.user import User
from app.schemas.part_schema import (
    PartCollaboratorResponse,
    PartCreate,
    PartListQueryParams,
    PartPaginatedResponse,
    PartResponse,
    PartSortBy,
    PartUpdate,
    SortOrder,
    TopWordsResponse,
)
from app.services.part_service import PartService
from app.services.security_service import get_current_active_user

router = APIRouter(prefix="/parts", tags=["parts"])

part_service = PartService()


@router.post("", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
async def create_part(
    part: PartCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> PartResponse:
    return await part_service.create_part(session, part, current_user)


@router.get("", response_model=PartPaginatedResponse)
async def list_parts(
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_active_user),
    visibility: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    name: Optional[List[str]] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Any:
    visibility_enum = PartVisibility(visibility.upper()) if visibility else None
    sort_by_enum = PartSortBy(sort_by) if sort_by else PartSortBy.created_at
    sort_order_enum = SortOrder(sort_order) if sort_order else SortOrder.desc
    params = PartListQueryParams(
        visibility=visibility_enum,
        is_active=is_active,
        name=name,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by_enum,
        sort_order=sort_order_enum,
        limit=limit,
        offset=offset,
    )
    result = await part_service.list_parts(session, current_user, params)
    return result


@router.get("/top-words", response_model=TopWordsResponse)
async def get_top_words(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
) -> TopWordsResponse:
    return await part_service.get_top_words_in_descriptions(session)


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
