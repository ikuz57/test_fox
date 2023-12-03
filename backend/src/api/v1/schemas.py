from typing import Optional, List
import datetime

from pydantic import BaseModel as PydanticBaseModel
from src.core import json
from pydantic import validator
from src.core.validators.pydantic import PydanticValidator


class BaseModel(PydanticBaseModel):
    class Config:
        json_loads = json.loads
        json_dumps = json.dumps


class MessageCreate(BaseModel):
    ticket_id: int
    content: str


class MessageReadShort(BaseModel):
    id: int
    user_id: Optional[int]
    content: str
    created_at: datetime.datetime


class MessageRead(MessageReadShort):
    ticket_id: int


class TicketRead(BaseModel):
    id: int
    user_id: Optional[int]
    status: str
    created_at: datetime.datetime


class TickeDetail(TicketRead):
    telegram_user_id: int
    messages: List[MessageReadShort]
    user_id: Optional[int]


class TicketUpdate(BaseModel):
    user_id: Optional[int] = None
    status: Optional[str] = None


class UserRead(BaseModel):
    id: int
    username: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserReadWithToken(BaseModel):
    access_token: str
    user: UserRead


class UserCreate(BaseModel):
    username: str
    password: str

    @validator('password')
    def validate_password(cls, v):
        return PydanticValidator.validate_password(v)

    @validator('username')
    def validate_username(cls, v):
        return PydanticValidator.validate_username(v)


class UserUpdate(BaseModel):
    password_new: Optional[str] = None
    password_old: Optional[str] = None

    @validator('password_new', 'password_old')
    def validate_password(cls, v):
        return PydanticValidator.validate_password(v)
