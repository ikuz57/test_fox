import os
from logging import config as logging_config

from pydantic_settings import BaseSettings

from dotenv import load_dotenv
from .logger import LOGGING

logging_config.dictConfig(LOGGING)
load_dotenv()


class Settings(BaseSettings):
    # настройки проекта
    PROJECT_NAME: str = 'sber_task'
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # настройки pyJWT
    SECRET: str = os.getenv('SECRET')

    # настройки ДБ
    DB_USER: str = os.getenv('POSTGRES_USER')
    DB_PASS: str = os.getenv('POSTGRES_PASSWORD')
    DB_HOST: str = os.getenv('POSTGRES_HOST')
    DB_PORT: str = os.getenv('POSTGRES_PORT')
    DB_NAME: str = os.getenv('POSTGRES_DB')

    # настройки Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'


settings = Settings()
