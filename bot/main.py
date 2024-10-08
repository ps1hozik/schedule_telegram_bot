import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from routers import router as main_router


async def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    dp = Dispatcher()
    dp.include_router(main_router)

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables")
        return

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
