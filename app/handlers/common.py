import logging

import app.database.requests as rq

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from app.handlers.states.auth_state import AuthState
from app.services.auth import fetch_token
from app.services.auth import get_authorization_url

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

        await message.reply("Нажми на кнопку для авторизации. После авторизации ты увидишь код на странице. "
                            "Используй команду /code и введи полученный код для завершения процесса.", reply_markup=keyboard)
        logger.info(f"Пользователю {message.from_user.id} отправлен URL для авторизации.")
    except Exception as e:
        await message.reply("Произошла ошибка при получении URL для авторизации. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в authorize_handler: {e}")


async def code_handler(message: Message, state: FSMContext):
    try:
        await message.reply("Пожалуйста, введите код, который вы получили после авторизации:")
        logger.info(f"Пользователь {message.from_user.id} запросил ввод кода.")
        await state.set_state(AuthState.waiting_for_code)
    except Exception as e:
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в code_handler: {e}")


async def process_code(message: Message, state: FSMContext):
    try:
        code_parts = message.text.split()
        if len(code_parts) != 2:
            await message.reply("Неверный формат кода. Пожалуйста, убедитесь, что вы ввели код в формате 'state code'.")
            return

        auth_state, code = code_parts
        tg_id = await rq.get_tg_id_by_state(auth_state)
        if await fetch_token(tg_id, auth_state, code):
            await message.reply("Авторизация успешно завершена!")
            logger.info(f"Пользователь {tg_id} успешно авторизован.")
        else:
            await message.reply("Не удалось завершить авторизацию. Пожалуйста, попробуйте снова.")
            logger.error(f"Не удалось завершить авторизацию для пользователя {tg_id}.")

        await state.clear()
    except Exception as e:
        await message.reply("Произошла ошибка при завершении авторизации. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в process_code: {e}")


