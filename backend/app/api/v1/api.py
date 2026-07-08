"""Agregador dos routers da versão 1 da API.

Novos routers de features (auth, missions, achievements, etc.) devem ser
incluídos aqui à medida que forem criados nas próximas EPICs.
"""

from fastapi import APIRouter

from app.api.v1.achievements import router as achievements_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.events import router as events_router
from app.api.v1.health import router as health_router
from app.api.v1.missions import router as missions_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(dashboard_router)
api_router.include_router(missions_router)
api_router.include_router(achievements_router)
api_router.include_router(events_router)
