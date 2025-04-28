from typing import Any, Generic, Optional, Type, TypeVar

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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
        if isinstance(obj_in, dict):
            data = obj_in
        else:
            data = obj_in.model_dump()
        db_obj = self.model(**data)
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
        if isinstance(obj_in, dict):
            data = obj_in
        else:
            data = obj_in.model_dump(exclude_unset=True)
        for field, value in data.items():
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

    async def exists_by_fields(
        self, session: AsyncSession, field_value_pairs: list[tuple[Any, Any]]
    ) -> Optional[tuple[Any, Any]]:
        if not field_value_pairs:
            return None

        conditions = [field == value for field, value in field_value_pairs]
        query = select(self.model).where(or_(*conditions))
        result = await session.execute(query)
        found = result.scalars().first()
        if not found:
            return None

        # Find which field matched
        for field, value in field_value_pairs:
            if getattr(found, field.key) == value:
                return field, value

        return None
