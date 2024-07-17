import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import TOKEN
from app.handlers import router
from app.database.models.base import async_main

logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    try:
        await async_main()
        dp.include_router(router)
        await dp.start_polling(bot)
    except Exception as exception:
        logger.error(f"Произошла ошибка в главной функции: {str(exception)}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Программа завершена по запросу пользователя.')
    except Exception as e:
        logger.error(f"Произошла ошибка при запуске программы: {str(e)}")
