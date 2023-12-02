import logging
from contextlib import asynccontextmanager

import orjson
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
# from redis.asyncio import Redis
from src.core.config import settings
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


# аутентификация и пользователи


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
    )
