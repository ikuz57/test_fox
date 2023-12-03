from aiogram import types, F, Router
from sqlalchemy import select, and_, or_
import requests

from app.db.models import Ticket, Message
from app.db.sqlalchemy import async_session_factory

router = Router()


@router.message(F.text)
async def get(message: types.Message):
    session = async_session_factory()
    async with session.begin():
        ticket = (
            await session.execute(
                select(
                    Ticket
                ).where(
                    and_(
                        Ticket.telegram_user_id == message.chat.id,
                        or_(Ticket.status == 'Открыт', Ticket.status == 'В работе')
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
                    "msg_content": new_message.content
                }
            )
        else:
            new_ticket = Ticket(
                telegram_user_id=message.chat.id,
                status='Открыт'
            )
            session.add(new_ticket)
            await session.flush()
            new_message = Message(
                ticket_id=new_ticket.id,
                user_id=None,
                content=message.text
            )
            session.add(new_message)

            await message.answer(
                'Ваше обращение зарегестрировано.\n'
                'К вам уже спешат на помощь.\n'
                f'Номер вашего обращения: {new_ticket.id}'
            )


async def notify_api_service(message_data):
    api_url = "http://backend:8000/api/v1/message/notify"
    requests.post(api_url, json=message_data)
