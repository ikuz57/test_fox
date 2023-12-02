import asyncio
import os

from dotenv import load_dotenv

# from aiogram.filters import Command
from aiogram import Bot

from app.logger import logger
from app.dispatcher import dp

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))


async def main() -> None:
    logger.info("START_BOT")
    # await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info('START BOT')
    asyncio.run(main())
