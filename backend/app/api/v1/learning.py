"""Router do módulo de Videoaulas (`/learning`).

Protegido por `Depends(get_current_user)` — qualquer papel autenticado
chega aqui; **qual** conteúdo cada um vê é decidido em `learning_service`
pelo público do curso, nunca pela rota. Assim a mesma API serve a Formação
de Pais (responsável) e, futuramente, a Preparação do Aluno (candidato).
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.learning import (
    CourseCard,
    CourseOverview,
    LessonDetail,
    ProgressUpdateRequest,
    ProgressUpdateResult,
)
from app.schemas.response import ApiResponse
from app.services import learning_service

router = APIRouter(prefix="/learning", tags=["Videoaulas"])


@router.get(
    "/courses",
    response_model=ApiResponse[list[CourseCard]],
    summary="Cursos disponíveis para o perfil autenticado",
)
async def list_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[CourseCard]]:
    data = await learning_service.list_courses(db, current_user)
    return ApiResponse(success=True, message="Cursos recuperados com sucesso.", data=data)


@router.get(
    "/courses/{slug}",
    response_model=ApiResponse[CourseOverview],
    summary="Visão geral do curso: módulos, aulas, progresso e próxima aula (sem vídeo)",
)
async def get_course_overview(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CourseOverview]:
    data = await learning_service.get_course_overview(db, current_user, slug)
    return ApiResponse(success=True, message="Curso recuperado com sucesso.", data=data)


@router.get(
    "/lessons/{lesson_id}",
    response_model=ApiResponse[LessonDetail],
    summary="Aula para assistir — a única resposta que carrega o vídeo",
)
async def get_lesson(
    lesson_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LessonDetail]:
    data = await learning_service.get_lesson(db, current_user, lesson_id)
    return ApiResponse(success=True, message="Aula recuperada com sucesso.", data=data)


@router.put(
    "/lessons/{lesson_id}/progress",
    response_model=ApiResponse[ProgressUpdateResult],
    summary="Grava a posição assistida; conclui a aula ao cruzar o limiar",
)
async def update_progress(
    lesson_id: uuid.UUID,
    payload: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ProgressUpdateResult]:
    data = await learning_service.update_progress(
        db, current_user, lesson_id, payload.position_seconds
    )
    message = "Aula concluída!" if data.just_completed else "Progresso salvo."
    return ApiResponse(success=True, message=message, data=data)
