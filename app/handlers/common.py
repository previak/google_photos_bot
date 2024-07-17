from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests as rq
from app.services.auth import fetch_token
from app.services.auth import get_authorization_url
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_handler(message: Message):
    try:
        await rq.set_user(message.from_user.id)
        await message.reply(
            "Привет! Отправь мне фото, и я загружу его в твой Google Photos. Используй команду /authorize для начала."
        )
        logger.info(f"Пользователь {message.from_user.id} зарегистрирован.")
    except Exception as e:
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в start_handler: {e}")


async def authorize_handler(message: Message):
    try:
        authorization_url = await get_authorization_url(message.from_user.id)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Авторизоваться', url=authorization_url)],
        ])

        await message.reply("Нажми на кнопку для авторизации.", reply_markup=keyboard)
        logger.info(f"Пользователю {message.from_user.id} отправлен URL для авторизации.")
    except Exception as e:
        await message.reply("Произошла ошибка при получении URL для авторизации. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в authorize_handler: {e}")


async def code_handler(message: Message):
    try:
        state, code = message.text.split()
        tg_id = await rq.get_tg_id_by_state(state)
        if await fetch_token(tg_id, state, code):
            await message.reply("Авторизация успешно завершена!")
            logger.info(f"Пользователь {tg_id} успешно авторизован.")
        else:
            await message.reply("Не удалось завершить авторизацию. Пожалуйста, попробуйте снова.")
            logger.error(f"Не удалось завершить авторизацию для пользователя {tg_id}.")
    except Exception as e:
        await message.reply("Произошла ошибка при завершении авторизации. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в code_handler: {e}")


