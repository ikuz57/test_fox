from fastapi import APIRouter, Depends, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.service.project import ProjectService, get_project_service

from .paginator import pagination
from .schemas import (ProjectCreate, ProjectDetail, ProjectReadShort,
                      ProjectUpdate)

# from src.service.user import auth_check


router = APIRouter()


@router.get(
        '/',
        description='Вывод всех существующих проектов c фильтрацией по user_id'
    )
# @auth_check
async def project_main(
    request: Request,
    sort: str = '-created_at',
    filter_status: int = Query(
        None,
        alias='filter[status]',
        description=(
            'status_id по которому будет производиться фильтрация проектов'
            )
    ),
    filter_manager: int = Query(
        None,
        alias='filter[manager]',
        description=(
            'manager_id по которому будет производиться фильтрация проектов'
            )
    ),
    filter_created_by: int = Query(
        None,
        alias='filter[created_by]',
        description=(
            'created_by по которому будет производиться фильтрация проектов'
            )
    ),
    filter_group: int = Query(
        None,
        alias='filter[group_id]',
        description=(
            'group_id по которому будет производиться фильтрация проектов'
            )
    ),
page_parameters: dict = Depends(pagination),
    project_service: ProjectService = Depends(get_project_service)
) -> JSONResponse:
    projects, total_projects = await project_service.get_project_pagination(
        sort=sort,
        filter_status = filter_status,
        filter_manager=filter_manager,
        filter_created_by=filter_created_by,
        filter_group=filter_group,
        page_size=page_parameters['page_size'],
        page_number=page_parameters['page_number'],
    )
    headers = {"total_projects": str(total_projects)}
    content = jsonable_encoder(projects)
    return JSONResponse(content=content, headers=headers)


@router.post(
    '/',
    description='Создание проекта'
)
# @auth_check
async def create(
    request: Request,
    project_data: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service)
) -> ProjectReadShort:
    new_id = await project_service.create(project_data)
    project = await project_service.get_project_by_id(new_id)
    return project

@router.get(
        '/{project_id}',
        description='Вывод информации по проекту'
    )
# @auth_check
async def project_details(
    request: Request,
    project_id: int,
    project_service: ProjectService = Depends(get_project_service)
) -> ProjectDetail:
    project = await project_service.get_project_by_id(project_id)
    return project


@router.patch(
        '/{project_id}',
        description='Обновление проекта по его id'
    )
# @auth_check
async def update(
    request: Request,
    project_data: ProjectUpdate,
    project_id: int,
    project_service: ProjectService = Depends(get_project_service)
) -> ProjectDetail:
    project_id = await project_service.update(project_id, project_data)
    project = await project_service.get_project_by_id(project_id)
    return project


@router.delete(
        '/{project_id}',
        description='Удаление проекта по id'
)
# @auth_check
async def delete(
    request: Request,
    project_id: int,
    project_service: ProjectService = Depends(get_project_service)
) -> ProjectDetail:
    await project_service.delete(project_id)
    return JSONResponse(content={'detail': 'Проект успешно удален'})
