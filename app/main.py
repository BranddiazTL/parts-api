from fastapi import FastAPI
from app.api.routes.auth_router import router as auth_router
from app.api.routes.user_router import router as user_router
from app.api.routes.health_router import router as health_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(health_router)
