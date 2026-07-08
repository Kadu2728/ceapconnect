"""Schemas de resposta do endpoint de health check."""

from pydantic import BaseModel


class HealthData(BaseModel):
    """Dado retornado pelo endpoint `GET /api/v1/health`."""

    status: str
    version: str
    database: str
