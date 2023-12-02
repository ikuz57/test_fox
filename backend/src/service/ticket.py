import logging
from functools import lru_cache
from typing import List
from fastapi import Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload
from sqlalchemy import func, desc

from src.api.v1.schemas import UserReadShort, GroupCreate, GroupRead, GroupUpdate
from src.api.v1.schemas import GroupReadShort
from src.db.models import Group, User, Project
from src.db.sqlalchemy import get_async_session


class GroupService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, group_data: GroupCreate) -> None:
        async with self.session.begin():
            project = await self.session.get(
                Project, group_data.project_id,
                options=(
                    selectinload(Project.groups),
                )
            )
            if not project:
                raise HTTPException(
                    status_code=404,
                    detail=f'Проект с id={group_data.project_id} не существует.'
                )

            new_group = Group(name=group_data.name)
            non_existent_users = []
            for user_id in group_data.users:
                user = await self.session.get(User, user_id)
                if user:
                    new_group.users.append(user)
                else:
                    non_existent_users.append(user_id)
            if non_existent_users:
                raise HTTPException(
                    status_code=404,
                    detail=f'Пользователей с id={non_existent_users} не существует.'
                )
            self.session.add(new_group)
            project.groups.append(new_group)
            logging.info(f'{project=}')
            logging.info(f'{new_group=}')
            await self.session.flush()
            new_id =new_group.id
            await self.session.commit()
            return new_id

    async def get_group_list(
        self,
        sort: str,
        filter_group: int,
        page_size: int,
        page_number: int
    ) -> List[GroupReadShort]:
        offset = (page_number - 1) * page_size
        sort_by = getattr(Group, sort.replace('-', ''), Group.id)
        async with self.session.begin():
            if filter_group:
                project = await self.session.get(Project, filter_group)
                if not project:
                    raise HTTPException(status_code=404, detail='Нет проекта с таким id')
                total_group = (await self.session.execute(
                    select(func.count('*')).select_from(Group).where(
                    Group.project_id == filter_group
                ))).scalar()
            else:
                total_group = (await self.session.execute(
                    select(func.count('*')).select_from(Group)
                )).scalar()
            query = select(
                    Group
                ).options(
                    selectinload(Group.users),
                    selectinload(Group.project)
                )
            if filter_group:
                query = query.where(
                    Group.project_id == filter_group
                )
            query = query.order_by(
                desc(sort_by) if sort.startswith('-') else sort_by
            ).offset(
                offset
            ).limit(
                page_size
            )
            groups = (await self.session.scalars(query)).all()
            group_list = []
            current_group = None
            for item in groups:
                if current_group is None or current_group.id != item.id:
                    if current_group is not None:
                        group_list.append(current_group)
                    current_group = GroupRead(
                        id=item.id,
                        name=item.name,
                        project_id=item.project_id,
                        users=[]
                    )
                    for user in item.users:
                        user_to_add = UserReadShort(
                            id=user.id,
                            first_name=user.first_name,
                            middle_name=user.middle_name,
                            last_name=user.last_name
                        )
                        current_group.users.append(user_to_add)
            if current_group is not None:
                group_list.append(current_group)
        return group_list, total_group


    async def get_group_by_id(self, group_id: str) -> GroupRead:
        async with self.session.begin():
            try:
                group = (
                    await self.session.scalars(
                        select(Group).where(
                            Group.id == group_id).options(selectinload(Group.users))
                    )
                ).one()
            except NoResultFound:
                raise HTTPException(status_code=404, detail='Группы с таким id не существует')
            group_return = GroupRead(
                id=group.id,
                name=group.name,
                users=[UserReadShort(
                    id=x.id,
                    first_name=x.first_name,
                    middle_name=x.middle_name,
                    last_name=x.last_name
                ) for x in group.users],
                project_id=group.project_id
            )
            return group_return

    async def update(self, group_id: int, group_data: GroupUpdate):
        if group_data:
            async with self.session.begin():
                group = (
                    await self.session.scalars(
                        select(Group).where(
                            Group.id == group_id).options(selectinload(Group.users))
                    )
                ).one()
                if group_data.name:
                    group.name = group_data.name
                if group_data.users:
                    non_existent_users = []
                    old_users = group.users
                    group.users.clear()
                    for user_id in group_data.users:
                        user = await self.session.get(User, user_id)
                        if user:
                            group.users.append(user)
                        else:
                            non_existent_users.append(user_id)
                    if non_existent_users:
                        group.users = old_users
                        raise HTTPException(
                            status_code=404,
                            detail=f'Пользователей с id={non_existent_users} не существует.'
                        )
                await self.session.commit()
                return
        raise HTTPException(status_code=400, detail='Пустой запрос')

    async def delete(self, group_id: int) -> None:

        async with self.session.begin():
            group = await self.session.get(Group, group_id)
            if not group:
                raise HTTPException(status_code=404, detail='Группы с таким id не существует')
        try:
                await self.session.delete(group)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f'{e}')
        else:
            await self.session.commit()

@lru_cache()
def get_group_service(
    session: AsyncSession = Depends(get_async_session),
) -> GroupService:
    return GroupService(session)
