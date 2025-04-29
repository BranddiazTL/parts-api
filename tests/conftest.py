from typing import AsyncGenerator

import httpx
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.api.dependencies import get_db_session as app_get_db_session
from app.core.config import settings
from app.main import app as main_app
from app.models import Base
from tests.factories.user_factory import UserFactory
from tests.fixtures.authorization import client_collaborator  # noqa: F401
from tests.fixtures.authorization import client_superuser  # noqa: F401
from tests.fixtures.authorization import client_user  # noqa: F401
from tests.fixtures.authorization import collaborator_token_headers  # noqa: F401
from tests.fixtures.authorization import superuser_token_headers  # noqa: F401
from tests.fixtures.authorization import user_token_headers  # noqa: F401

TEST_DATABASE_URL = settings.database_url.replace("_db", "_test_db")
DEFAULT_POSTGRES_URL = settings.database_url.replace(settings.POSTGRES_DB, "postgres")
SYNC_DEFAULT_POSTGRES_URL = DEFAULT_POSTGRES_URL.replace("+asyncpg", "")
SYNC_TEST_DATABASE_URL = TEST_DATABASE_URL.replace("+asyncpg", "")
TEST_DB_NAME = settings.POSTGRES_DB.replace("_db", "_test_db")

# Create one engine for admin tasks, one for test DB operations
sync_admin_engine = create_engine(
    SYNC_DEFAULT_POSTGRES_URL, isolation_level="AUTOCOMMIT"
)
sync_test_engine = create_engine(SYNC_TEST_DATABASE_URL)


def create_test_db_if_not_exists():
    """Creates the test database if it doesnt exist."""
    try:
        with sync_admin_engine.connect() as conn:
            db_exists = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname='{TEST_DB_NAME}'")
            ).scalar()
            if not db_exists:
                print(f"Database '{TEST_DB_NAME}' does not exist. Creating...")
                conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
                print(f"Database '{TEST_DB_NAME}' created.")
            else:
                print(f"Database '{TEST_DB_NAME}' already exists.")
    except ProgrammingError as e:
        print(f"DB Creation/Check Error: {e}")
    except Exception as e:
        print(f"Unexpected error during DB creation/check: {e}")
        raise
    finally:
        sync_admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def manage_test_db_schema():
    """Creates tables before session, drop them after."""
    create_test_db_if_not_exists()
    print(f"Creating tables in '{TEST_DB_NAME}' based on Base.metadata...")
    try:
        Base.metadata.create_all(bind=sync_test_engine)
        print("Tables created.")
        yield
    finally:
        print(f"Dropping tables from '{TEST_DB_NAME}'...")
        Base.metadata.drop_all(bind=sync_test_engine)
        print("Tables dropped.")
        sync_test_engine.dispose()


@pytest.fixture(scope="session")
async def async_engine():
    """Provide an async engine connected to the test database."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for each test."""
    async_session_factory = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_factory() as session:
        await session.begin_nested()
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async test client with overridden DB session dependency."""

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    main_app.dependency_overrides[app_get_db_session] = override_get_db_session

    transport = httpx.ASGITransport(app=main_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    main_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def authenticated_client(
    client: httpx.AsyncClient, db_session: AsyncSession
) -> httpx.AsyncClient:
    """Provide an authenticated async client."""

    raw_password = "testpassword123"
    user = await db_session.run_sync(
        lambda sync_sess: UserFactory.create(session=sync_sess, password=raw_password)
    )
    await db_session.commit()

    login_data = {"username": user.email, "password": raw_password}

    res = await client.post("/auth/token", data=login_data)

    if res.status_code != 200:
        print(f"Login failed with status {res.status_code}: {res.text}")
        raise RuntimeError(
            f"Could not log in user {user.email} for authenticated client fixture."
        )

    token_data = res.json()
    token = token_data.get("access_token")
    if not token:
        raise RuntimeError(f"Access token not found in login response: {token_data}")

    client.headers["Authorization"] = f"Bearer {token}"

    return client
