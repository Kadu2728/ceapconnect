"""Exceções de negócio e handlers globais.

Toda exceção previsível (recurso não encontrado, conflito, dado inválido
etc.) deve ser levantada como uma subclasse de `AppException` a partir da
camada de services. Os handlers registrados aqui garantem que a resposta
segue sempre o envelope padrão da API e que nenhum detalhe interno
(stack trace, mensagem de driver de banco, etc.) vaza para o cliente.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.response import ApiResponse

logger = logging.getLogger("ceap_connect")


class AppException(Exception):
    """Exceção base para erros de negócio previsíveis.

    Deve ser levantada pelos services e nunca pelos routers diretamente.
    """

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Recurso não encontrado.") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class BadRequestException(AppException):
    def __init__(self, message: str = "Requisição inválida.") -> None:
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Não autenticado.") -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Acesso não permitido.") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflito com o estado atual do recurso.") -> None:
        super().__init__(message, status.HTTP_409_CONFLICT)


class UnprocessableEntityException(AppException):
    def __init__(self, message: str = "Não foi possível processar os dados enviados.") -> None:
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


def _error_response(message: str, status_code: int) -> JSONResponse:
    payload = ApiResponse(success=False, message=message, data=None, meta=None)
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    """Registra todos os exception handlers globais na instância do FastAPI."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        return _error_response(exc.message, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(
            "Dados de entrada inválidos.",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _error_response(str(exc.detail), exc.status_code)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro interno não tratado", exc_info=exc)
        return _error_response(
            "Erro interno do servidor. Tente novamente mais tarde.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
