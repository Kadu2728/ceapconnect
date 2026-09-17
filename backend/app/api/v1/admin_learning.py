"""Router da gestão de cursos no painel admin (`/admin/learning/*`).

Admin-only (`get_current_admin`), como o resto do catálogo gerenciável
(recompensas). Coordenador não edita conteúdo — só consome pela gestão.
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.admin_learning import (
    AdminCourseDetail,
    AdminCourseItem,
    AdminCourseListResponse,
    AdminCourseWrite,
    AdminLessonItem,
    AdminLessonWrite,
    AdminModuleItem,
    AdminModuleWrite,
)
from app.schemas.response import ApiResponse
from app.services import admin_learning_service

router = APIRouter(prefix="/admin/learning", tags=["Admin · Videoaulas"])


@router.get(
    "/courses", response_model=ApiResponse[AdminCourseListResponse], summary="Gestão de cursos"
)
async def list_courses(
    _admin: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)
) -> ApiResponse[AdminCourseListResponse]:
    data = await admin_learning_service.list_courses(db)
    return ApiResponse(success=True, message="Cursos recuperados com sucesso.", data=data)


@router.get(
    "/courses/{course_id}",
    response_model=ApiResponse[AdminCourseDetail],
    summary="Curso com módulos e aulas, para edição",
)
async def get_course(
    course_id: uuid.UUID,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminCourseDetail]:
    data = await admin_learning_service.get_course_detail(db, course_id)
    return ApiResponse(success=True, message="Curso recuperado com sucesso.", data=data)


@router.post(
    "/courses",
    response_model=ApiResponse[AdminCourseItem],
    status_code=status.HTTP_201_CREATED,
    summary="Cria um curso",
)
async def create_course(
    payload: AdminCourseWrite,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminCourseItem]:
    data = await admin_learning_service.create_course(db, payload)
    return ApiResponse(success=True, message="Curso criado com sucesso.", data=data)


@router.patch(
    "/courses/{course_id}", response_model=ApiResponse[AdminCourseItem], summary="Atualiza um curso"
)
async def update_course(
    course_id: uuid.UUID,
    payload: AdminCourseWrite,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminCourseItem]:
    data = await admin_learning_service.update_course(db, course_id, payload)
    return ApiResponse(success=True, message="Curso atualizado com sucesso.", data=data)


@router.post(
    "/courses/{course_id}/modules",
    response_model=ApiResponse[AdminModuleItem],
    status_code=status.HTTP_201_CREATED,
    summary="Cria um módulo no curso",
)
async def create_module(
    course_id: uuid.UUID,
    payload: AdminModuleWrite,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminModuleItem]:
    data = await admin_learning_service.create_module(db, course_id, payload)
    return ApiResponse(success=True, message="Módulo criado com sucesso.", data=data)


@router.patch(
    "/modules/{module_id}",
    response_model=ApiResponse[AdminModuleItem],
    summary="Atualiza um módulo",
)
async def update_module(
    module_id: uuid.UUID,
    payload: AdminModuleWrite,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminModuleItem]:
    data = await admin_learning_service.update_module(db, module_id, payload)
    return ApiResponse(success=True, message="Módulo atualizado com sucesso.", data=data)


@router.post(
    "/modules/{module_id}/lessons",
    response_model=ApiResponse[AdminLessonItem],
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma aula no módulo",
)
async def create_lesson(
    module_id: uuid.UUID,
    payload: AdminLessonWrite,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminLessonItem]:
    data = await admin_learning_service.create_lesson(db, module_id, payload)
    return ApiResponse(success=True, message="Aula criada com sucesso.", data=data)


@router.patch(
    "/lessons/{lesson_id}", response_model=ApiResponse[AdminLessonItem], summary="Atualiza uma aula"
)
async def update_lesson(
    lesson_id: uuid.UUID,
    payload: AdminLessonWrite,
    _admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AdminLessonItem]:
    data = await admin_learning_service.update_lesson(db, lesson_id, payload)
    return ApiResponse(success=True, message="Aula atualizada com sucesso.", data=data)
