from aiogram import types, F

from sqlalchemy import select

from .dispatcher import dp

from ..db.sqlalchemy import get_async_session
from ..db.models import Ticket, Message


@dp.message(F.text)
async def get(message: types.Message):
    session = await get_async_session()
    async with session.begin():
        ticket = (
            await session.select(
                Ticket.status
            ).where(
                Ticket.telegram_user_id == message.chat.id | 
                Ticket.status == 'Открыт'
            )
        ).scalar()
        if ticket:
            new_message = Message(
                ticket_id=ticket.id,
                user_id=None,
                content=message.text
            )
            session.add(new_message)
        else:
            new_ticket = Ticket(
                telegram_user_id=message.chat.id,
                status='Открыт'
            )
            session.add(new_ticket)
            session.flush()
            new_message = Message(
                ticket_id=new_ticket.id,
                user_id=None,
                content=message.text
            )
            session.add(new_message)
    await message.answer('Ваша жалоба услышена')
