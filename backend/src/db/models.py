import datetime
from typing import Annotated, List, Optional

from sqlalchemy import TIMESTAMP, ForeignKey, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from fastapi_users.db import SQLAlchemyBaseUserTableUUID


created_at = Annotated[datetime.datetime, mapped_column(
    TIMESTAMP(timezone=True),
    server_default=text("TIMEZONE('utc', now())")
)]
updated_at = Annotated[datetime.datetime, mapped_column(
    TIMESTAMP(timezone=True),
    server_default=text("TIMEZONE('utc', now())"),
    onupdate=datetime.datetime.utcnow
)]

timestamp = Annotated[datetime.date, mapped_column(
    TIMESTAMP(timezone=True)
)]


# Base: DeclarativeMeta = DeclarativeBase()
class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    ticket: Mapped[list['Ticket']] = relationship(
        back_populates='tickets', uselist=True, secondary='ticket_assignments'
    )


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(unique=True)
    status: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.ticket_id"))
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.uuid'))
    # в телеграмме ограничение на пост с медиа и файлами 1024 символа
    content: Mapped[str] = mapped_column(String(1024))
    timestamp: Mapped[Optional[timestamp]]


class TicketAssignment(Base):
    __tablename__ = "ticket_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("user.uuid"))
