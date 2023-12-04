import requests
from aiogram import F, Router, types
from aiogram.filters import Command
from app.db.models import File, Message, Scheduler, Ticket
from app.db.sqlalchemy import async_session_factory
from sqlalchemy import and_, or_, select

FILE_PATH: str = '/fox_test/file_storage'

router = Router()


@router.message(F.text, Command('start'))
async def start(message: types.Message):
    help = (
        'Добро пожаловать, я бот для регистрации обращений foxbot.\n'
        'Что бы оставить обращение для нашей службы поддержки просто напишите '
        'в чат что у вас случилось.'
    )
    await message.answer(help)


@router.message(F.text)
async def get_msg(message: types.Message):
    session = async_session_factory()
    async with session.begin():
        ticket = (
            await session.execute(
                select(
                    Ticket
                ).where(
                    and_(
                        Ticket.telegram_user_id == message.chat.id,
                        or_(Ticket.status_id == 1, Ticket.status_id == 2)
                    )
                )
            )
        ).scalar()
        if ticket:
            new_message = Message(
                ticket_id=ticket.id,
                user_id=None,
                content=message.text
            )
            session.add(new_message)
            await session.flush()
            await notify_api_service(
                {
                    "ticket_id": ticket.id,
                    "msg_id": new_message.id,
                    "content": new_message.content
                }
            )
        else:
            scheduler = (await session.execute(
                select(
                    Scheduler
                ).where(
                    (Scheduler.telegram_user_id == message.chat.id)
                )
            )).scalar()
            new_ticket = Ticket(
                telegram_user_id=message.chat.id,
                status_id=1,
                user_id=scheduler.user_id if scheduler else None
            )
            session.add(new_ticket)
            await session.flush()
            new_message = Message(
                ticket_id=new_ticket.id,
                user_id=None,
                content="Пользователь прикрепил файл: file_id={}"
            )
            session.add(new_message)
            await message.answer(
                'Ваше обращение зарегестрировано.\n'
                'К Вам уже спешат на помощь!\n'
                f'Номер вашего обращения: {new_ticket.id}'
            )


@router.message()
async def get_file(
    message: types.Message
):
    if message.content_type == 'document':
        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path
        file_name = message.document.file_name
        session = async_session_factory()
        async with session.begin():
            ticket = (
                await session.execute(
                    select(
                        Ticket
                    ).where(
                        and_(
                            Ticket.telegram_user_id == message.chat.id,
                            or_(Ticket.status_id == 1, Ticket.status_id == 2)
                        )
                    )
                )
            ).scalar()
            file_extension = file_name.split('.')[-1]
            new_file = File(
                name=file_name,
                ticket_id=ticket.id
            )
            new_file.created_by = None
            session.add(new_file)
            await session.flush()
            file_id = new_file.id
            path_to_save = f'{FILE_PATH}/{file_id}.{file_extension}'
            await message.bot.download_file(file_path, path_to_save)
            new_message = Message(
                ticket_id=ticket.id,
                user_id=None,
                content=f"Пользователь прикрепил файл: file_id={file_id}"
            )
            await session.flush()
            await notify_api_service(
                {
                    "ticket_id": ticket.id,
                    "msg_id": new_message.id,
                    "content": new_message.content
                }
            )
            await session.commit()


async def notify_api_service(message_data):
    api_url = "http://backend:8000/api/v1/message/notify"
    requests.post(api_url, json=message_data)
