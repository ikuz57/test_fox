import base64
from fastapi import APIRouter, Depends, Query, Request, WebSocket
from fastapi import WebSocketDisconnect, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.service.ticket import get_ticket_service, TicketService
from src.api.v1.schemas import TickeDetail, TicketUpdate, TicketRead
from src.core.connections import TempConnection
from .paginator import pagination
from src.service.user import auth_check
from src.service.message import get_message_service, MessageService
from src.service.user import get_user_manager, UserManager
from src.api.v1.schemas import MessageCreate
from src.core.config import settings
import requests
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

router = APIRouter()


@router.get(
        '/',
        description='Вывод списка тасков',
    )
@auth_check
async def get_list(
    request: Request,
    sort: str = '-created_at',
    filter_status: str = Query(
        None,
        alias='filter[status]',
        description=(
            'status по которому будет производиться фильтрация проектов'
            )
    ),
    filter_user: int = Query(
        None,
        alias='filter[user]',
        description=(
            'user_id по которому будет производиться фильтрация проектов'
            )
    ),
    page_parameters: dict = Depends(pagination),
    ticket_service: TicketService = Depends(get_ticket_service)
) -> JSONResponse:
    tickets, total_projects = await ticket_service.get_pagination(
        sort=sort,
        filter_status=filter_status,
        filter_user=filter_user,
        page_size=page_parameters['page_size'],
        page_number=page_parameters['page_number'],
    )
    headers = {"total_tickets": str(total_projects)}
    content = jsonable_encoder(tickets)
    return JSONResponse(content=content, headers=headers)


@router.get(
        '/{ticket_id}',
        description='Вывод детальной информации по тикету'
    )
@auth_check
async def project_details(
    request: Request,
    ticket_id: int,
    ticket_service: TicketService = Depends(get_ticket_service)
) -> TickeDetail:
    ticket = await ticket_service.get_by_id(ticket_id)
    return ticket


@router.patch(
        '/{ticket_id}',
        description='Обновление тикета по его id'
    )
@auth_check
async def update(
    request: Request,
    ticket_data: TicketUpdate,
    ticket_id: int,
    ticket_service: TicketService = Depends(get_ticket_service)
) -> TicketRead:
    await ticket_service.update(ticket_id, ticket_data)
    ticket = await ticket_service.get_by_id(ticket_id)
    return ticket


@router.websocket(
        "/ws/{ticket_id}"
    )
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_id: int,
    message_service: MessageService = Depends(get_message_service)
):
    await websocket.accept()
    # Сохраняем соединение
    await websocket.send_text("Создано соединение")
    TempConnection.connections[ticket_id] = websocket
    user_id = None
    try:
        while True:
            data = await websocket.receive_text()
            if data.startswith('Authorization: '):
                access_token = data.split(": ")[1]
                if not access_token:
                    raise HTTPException(
                        status_code=401,
                        detail='Требуется аутентификация'
                    )
                try:
                    data = jwt.decode(access_token, settings.SECRET, algorithms='HS256')
                except ExpiredSignatureError:
                    # Генерируем исключение HTTPException для случая истекшего токена
                    raise HTTPException(status_code=403, detail='токен истек')
                except InvalidTokenError as e:
                    # Генерируем исключение HTTPException для случая недействительного
                    # токена
                    raise HTTPException(
                        status_code=401, detail=f'токен недействителен, {str(e)}'
                    )
                except Exception as e:
                    # Генерируем общее исключение для других ошибок
                    raise HTTPException(
                        status_code=500, detail=f'ошибка при проверке токена: {str(e)}'
                    )
                user_id = int(data['user_id'])
                data = None
                await websocket.send_text("Авторизация пройдена")
            # if data.startswith("file:"):
            #     file_data = data.split(":")[1]
            #     file_content, file_name = file_data.split(";")
            #     requests.post(self.api_url + method, data={'chat_id': chat_id}, files={'document': document})
            #     # Сохраняем файл на сервере
            #     # await save_file_from_base64(file_content, file_name)
                # await websocket.send_text(f"File '{file_name}' received and saved.")
            if user_id and data is not None:
                await message_service.create(
                    MessageCreate(
                        ticket_id=ticket_id,
                        content=data,
                    ),
                    user_id
                )
                await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        del TempConnection.connections[ticket_id]


async def save_file_from_base64(self, base64_content: str, file_name: str):
    # Декодируем base64 строку в байты
    file_content = base64.b64decode(base64_content)
    file_path = settings.FILE_PATH + file_name
    # Сохраняем файл на сервере
    with open(file_path, "wb") as f:
        f.write(file_content)
