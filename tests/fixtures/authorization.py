from typing import AsyncGenerator

import httpx
import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.security_service import create_access_token
from tests.constants.user import UserTestConstants
from tests.factories.user_factory import UserFactory

fake = Faker()


@pytest.fixture(scope="function")
async def superuser_token_headers(db_session: AsyncSession) -> dict[str, str]:
    """Generate token headers for a superuser (Role Admin)."""
    user = UserFactory.create(
        session=db_session,
        email=UserTestConstants.CLIENT_SUPERUSER_EMAIL,
        password=UserTestConstants.CLIENT_SUPERUSER_PASSWORD,
        is_superuser=True,
    )
    await db_session.commit()

    token_data = {"sub": user.email}
    access_token = create_access_token(data=token_data)
    headers = {"Authorization": f"Bearer {access_token}"}

    return headers


async def _generate_token_headers(
    db_session: AsyncSession,
    password: str,
    is_superuser: bool = False,
) -> dict[str, str]:
    test_email = fake.email()
    test_username = fake.user_name()[:50]

    user = UserFactory.create(
        session=db_session,
        email=test_email,
        username=test_username,
        password=password,
        is_superuser=is_superuser,
    )
    await db_session.commit()

    token_data = {"sub": user.email}
    access_token = create_access_token(data=token_data)

    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
async def user_token_headers(db_session: AsyncSession) -> dict[str, str]:
    """Generate token headers for a regular user."""
    return await _generate_token_headers(
        db_session, UserTestConstants.CLIENT_USER_PASSWORD, is_superuser=False
    )


@pytest.fixture(scope="function")
async def collaborator_token_headers(db_session: AsyncSession) -> dict[str, str]:
    """Generate token headers for collaborator regular user."""
    return await _generate_token_headers(
        db_session, "collaborator_password", is_superuser=False
    )


async def _client_with_token_headers(
    client: httpx.AsyncClient, token_headers: dict[str, str]
) -> AsyncGenerator[httpx.AsyncClient, None]:
    client.headers.update(token_headers)
    yield client
    for key in token_headers:
        if key in client.headers:
            del client.headers[key]


@pytest.fixture(scope="function")
async def client_user(
    client: httpx.AsyncClient, user_token_headers: dict[str, str]
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Return an AsyncClient with regular user token headers."""
    async for c in _client_with_token_headers(client, user_token_headers):
        yield c


@pytest.fixture(scope="function")
async def client_collaborator(
    client: httpx.AsyncClient, collaborator_token_headers: dict[str, str]
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Return an AsyncClient with collaborator token headers."""
    async for c in _client_with_token_headers(client, collaborator_token_headers):
        yield c


@pytest.fixture(scope="function")
async def client_superuser(
    client: httpx.AsyncClient, superuser_token_headers: dict[str, str]
) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Return an AsyncClient with superuser token headers."""
    async for c in _client_with_token_headers(client, superuser_token_headers):
        yield c
