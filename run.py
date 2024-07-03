import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import TOKEN
from app.handlers import router
from server import start_webhook

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def on_startup():
    await start_webhook(dp, bot)


async def main():
    dp.include_router(router)
    loop = asyncio.get_event_loop()
    await loop.create_task(on_startup())
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
