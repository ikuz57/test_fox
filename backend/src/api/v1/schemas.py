import uuid
from fastapi_users import schemas

from pydantic import BaseModel as PydanticBaseModel
from pydantic import EmailStr, ValidationError, validator
from src.core import json
from src.core.validators.pydantic import PydanticValidator


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
