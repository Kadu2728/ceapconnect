"""Ponto de entrada da aplicação FastAPI.

Responsável apenas por instanciar o app, registrar middlewares, exception
handlers e os routers versionados. Nenhuma lógica de negócio deve viver
neste módulo.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title=settings.app_name,
    description=(
        "API da plataforma CEAP Connect — Candidate Experience gamificada "
        "para o processo seletivo do CEAP."
    ),
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")
