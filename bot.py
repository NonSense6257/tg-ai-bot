import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import TELEGRAM_TOKEN
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Бот запущено")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
