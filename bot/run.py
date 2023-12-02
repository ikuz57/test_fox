import asyncio
import os
import logging

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from app.handler import ticket

load_dotenv()

logging.basicConfig(level=logging.DEBUG)


async def main() -> None:
    logging.info("START_BOT")
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(ticket.router)
    # await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.info('START BOT')
    asyncio.run(main())
