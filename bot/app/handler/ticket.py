from aiogram import types, F, Router
from sqlalchemy import select, and_

from app.db.models import Ticket, Message
from app.db.sqlalchemy import get_async_session
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
                        Ticket.status == 'Открыт'
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
        await session.commit()
    await message.answer('Ваша жалоба услышена')
