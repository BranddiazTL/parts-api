import random

import pytest
from faker import Faker
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.part import Part, PartVisibility
from app.models.user import User
from app.schemas.part_schema import PartCreate, PartUpdate
from app.services.part_service import PartService
from tests.factories.part_factory import PartFactory
from tests.factories.user_factory import UserFactory

pytestmark = pytest.mark.asyncio

fake = Faker()
part_service = PartService()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = UserFactory.create(session=db_session)
    await db_session.commit()
    return user


@pytest.fixture
async def test_part(db_session: AsyncSession, test_user: User) -> Part:
    part = PartFactory.create(session=db_session, owner=test_user)
    await db_session.commit()
    return part


async def test_create_part(db_session: AsyncSession, test_user: User):
    part_data = PartCreate(
        name=f"Created Part {fake.word()}",
        sku=f"SKU-CREATE-{random.randint(1000, 9999)}-{fake.lexify('????').upper()}",
        description=fake.sentence(),
        weight_ounces=random.randint(1, 50),
        visibility=PartVisibility.PRIVATE,
    )

    created_part = await part_service.create_part(
        session=db_session, part_data=part_data, owner=test_user
    )

    assert created_part is not None
    assert created_part.name == part_data.name
    assert created_part.sku == part_data.sku
    assert created_part.description == part_data.description
    assert created_part.weight_ounces == part_data.weight_ounces
    assert created_part.visibility == part_data.visibility
    assert created_part.owner_id == test_user.id


async def test_get_part(db_session: AsyncSession, test_part: Part, test_user: User):
    retrieved_part = await part_service.get_part(
        session=db_session, part_id=str(test_part.id), user=test_user
    )

    assert retrieved_part is not None
    assert retrieved_part.id == test_part.id
    assert retrieved_part.name == test_part.name
    assert retrieved_part.sku == test_part.sku
    assert retrieved_part.owner_id == test_user.id


async def test_update_part(db_session: AsyncSession, test_part: Part, test_user: User):
    update_data = PartUpdate(
        name="Updated Part Name",
        description="Updated description.",
        visibility=PartVisibility.PUBLIC,
    )

    updated_part = await part_service.update_part(
        session=db_session,
        part_id=str(test_part.id),
        part_data=update_data,
        user=test_user,
    )

    assert updated_part is not None
    assert updated_part.id == test_part.id
    assert updated_part.name == update_data.name
    assert updated_part.description == update_data.description
    assert updated_part.visibility == update_data.visibility
    assert updated_part.sku == test_part.sku  # Should not change
    assert updated_part.owner_id == test_user.id

    # Verify persistence
    refetched_part = await part_service.get_part(
        session=db_session, part_id=str(test_part.id), user=test_user
    )
    assert refetched_part.name == update_data.name
    assert refetched_part.visibility == update_data.visibility


async def test_delete_part(db_session: AsyncSession, test_part: Part, test_user: User):
    part_id_to_delete = str(test_part.id)

    await part_service.delete_part(
        session=db_session, part_id=part_id_to_delete, user=test_user
    )

    # Verify is gone
    with pytest.raises(HTTPException) as exc_info:
        await part_service.get_part(
            session=db_session, part_id=part_id_to_delete, user=test_user
        )

    assert exc_info.value.status_code == 404
