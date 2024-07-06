import os
from aiogram.types import Message

import app.database.requests as rq
from app.services.photo import upload_photo


async def photo_handler(message: Message):
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
        await message.reply("Фото было успешно загружено.")
    else:
        await message.reply("Произошла ошибка при загрузке фото.")
