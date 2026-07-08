"""Envelope de resposta padrão da API, conforme API_GUIDELINES.md.

Toda rota deve retornar (direta ou indiretamente, via response_model)
uma instância de `ApiResponse`, garantindo o formato consistente:
`{ success, message, data, meta }`.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class Meta(BaseModel):
    """Metadados adicionais da resposta (ex.: paginação)."""

    page: int | None = None
    page_size: int | None = None
    total: int | None = None
    total_pages: int | None = None


class ApiResponse(BaseModel, Generic[DataT]):
    """Envelope padrão de resposta da API."""

    success: bool
    message: str
    data: DataT | None = None
    meta: Meta | None = None
