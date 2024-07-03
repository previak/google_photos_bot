import os

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from auth import get_authorization_url, upload_photo, user_creds

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(
        "Привет! Отправь мне фото, и я загружу его в твой Google Photos. Используй команду /authorize для начала."
    )


@router.message(Command('authorize'))
async def cmd_authorize(message: Message):
    authorization_url = get_authorization_url(message.from_user.id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Авторизоваться', url=authorization_url)],
    ])

    await message.reply(f"Нажми на кнопку для авторизации.", reply_markup=keyboard)


@router.message(Command('photo'))
async def cmd_photo(message: Message):
    if message.from_user.id not in user_creds:
        await message.reply("Пожалуйста, сначала авторизуйтесь с помощью команды /authorize")
        return

    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_path = file_info.file_path
    destination = f'{photo.file_id}.jpg'

    await message.bot.download_file(file_path, destination)

    response = upload_photo(message.from_user.id, destination)
    os.remove(destination)

    if response:
        await message.reply(f"Фото было успешно загружено.")
    else:
        await message.reply("Произошла ошибка при загрузке фото.")
