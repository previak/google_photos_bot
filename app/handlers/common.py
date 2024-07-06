from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests as rq
from app.services.auth import get_authorization_url


async def start_handler(message: Message):
    await rq.set_user(message.from_user.id)
    await message.reply(
        "Привет! Отправь мне фото, и я загружу его в твой Google Photos. Используй команду /authorize для начала."
    )


async def authorize_handler(message: Message):
    authorization_url = await get_authorization_url(message.from_user.id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Авторизоваться', url=authorization_url)],
    ])

    await message.reply("Нажми на кнопку для авторизации.", reply_markup=keyboard)
