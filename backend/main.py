# from contextlib import asynccontextmanager

import orjson
import uvicorn

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import ORJSONResponse

from fastapi.responses import HTMLResponse

from src.core.config import settings
from src.api.v1 import ticket, message, auth
from src.core.connections import TempConnection
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from src.service.user import auth_check
from src.service.message import get_message_service, MessageService
from src.api.v1.schemas import MessageCreate


# from redis.asyncio import Redis
# from src.db import redis


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     redis.redis = await Redis(
#         host=settings.REDIS_HOST, port=settings.REDIS_PORT
#     )
#     yield
#     await redis.redis.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse
    # lifespan=lifespan
)


# авторизация и аутентификация
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

# наши тикеты
app.include_router(ticket.router, prefix="/api/v1/ticket", tags=["ticket"])
app.include_router(message.router, prefix="/api/v1/message", tags=["message"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
    )
