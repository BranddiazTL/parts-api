from typing import TypeVar, Generic, Type, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.core.config import settings

T = TypeVar("T")

engine = create_async_engine(settings.database_url, echo=False, future=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class BaseRepository(Generic[T]):
    """Generic base repository for CRUD operations."""

    def __init__(self, model: Type[T]):
        """Initialize with the SQLAlchemy model class."""
        self.model = model

    async def get(self, session: AsyncSession, obj_id: Any) -> Optional[T]:
        """Retrieve an object by its primary key."""
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id)  # type: ignore
        )
        return result.scalars().first()

    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100):
        """Retrieve all objects with pagination."""
        result = await session.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, session: AsyncSession, obj_in: Any) -> T:
        """Create a new object from a Pydantic schema or dict."""
        db_obj = self.model(**obj_in.dict())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self, session: AsyncSession, obj_id: Any, obj_in: Any
    ) -> Optional[T]:
        """Update an existing object by its primary key."""
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id)  # type: ignore
        )
        db_obj = result.scalars().first()
        if not db_obj:
            return None
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, obj_id: Any) -> bool:
        """Delete an object by its primary key."""
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id)  # type: ignore
        )
        db_obj = result.scalars().first()
        if not db_obj:
            return False
        await session.delete(db_obj)
        await session.commit()
        return True
