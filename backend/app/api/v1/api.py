"""Agregador dos routers da versão 1 da API.

Novos routers de features (auth, missions, achievements, etc.) devem ser
incluídos aqui à medida que forem criados nas próximas EPICs.
"""

from fastapi import APIRouter

from app.api.v1.achievements import router as achievements_router
from app.api.v1.admin import router as admin_router
from app.api.v1.admin_funnel import router as admin_funnel_router
from app.api.v1.admin_risk import router as admin_risk_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.documents import router as documents_router
from app.api.v1.events import router as events_router
from app.api.v1.health import router as health_router
from app.api.v1.internal import router as internal_router
from app.api.v1.missions import router as missions_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.onboarding import router as onboarding_router
from app.api.v1.profile import router as profile_router
from app.api.v1.push import router as push_router
from app.api.v1.rewards import router as rewards_router
from app.api.v1.simulados import router as simulados_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(profile_router)
api_router.include_router(dashboard_router)
api_router.include_router(documents_router)
api_router.include_router(missions_router)
api_router.include_router(achievements_router)
api_router.include_router(events_router)
api_router.include_router(rewards_router)
api_router.include_router(simulados_router)
api_router.include_router(notifications_router)
api_router.include_router(admin_router)
api_router.include_router(admin_risk_router)
api_router.include_router(admin_funnel_router)
api_router.include_router(internal_router)
api_router.include_router(assistant_router)
api_router.include_router(onboarding_router)
api_router.include_router(push_router)
