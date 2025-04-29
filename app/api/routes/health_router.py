from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db_session

router = APIRouter(prefix="/health", tags=["health"])

db_dependency = Depends(get_db_session)


@router.get("")
async def health_check() -> dict:
    """Basic health check endpoint."""
    return {"status": "healthy"}


@router.get("/db")
async def db_health(session: AsyncSession = db_dependency) -> dict:
    """Database connection health check."""
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "database connected"}
    except Exception as e:
        return {"status": "database error", "detail": str(e)}
