import os
import app.database.requests as rq

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from app.service import get_authorization_url, upload_photo

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.reply(
        "Привет! Отправь мне фото, и я загружу его в твой Google Photos. Используй команду /authorize для начала.")



@router.message(Command('authorize'))
async def cmd_authorize(message: Message):
    authorization_url = await get_authorization_url(message.from_user.id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Авторизоваться', url=authorization_url)],
    ])

    await message.reply(f"Нажми на кнопку для авторизации.", reply_markup=keyboard)


@router.message(Command('photo'))
async def cmd_photo(message: Message):
    user_creds = await rq.get_user_credentials(message.from_user.id)

    if not user_creds:
        await message.reply("Пожалуйста, сначала авторизуйтесь с помощью команды /authorize")
        return

    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_path = file_info.file_path
    destination = f'{photo.file_id}.jpg'

    await message.bot.download_file(file_path, destination)

    response = await upload_photo(message.from_user.id, destination)
    os.remove(destination)

    if response:
        await message.reply(f"Фото было успешно загружено.")
    else:
        await message.reply("Произошла ошибка при загрузке фото.")
