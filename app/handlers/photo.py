import os
import logging

import app.database.requests as rq

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.handlers.states.photo_upload_state import PhotoUploadState
from app.services.photo import upload_photo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_photo_upload(message: Message, state: FSMContext):
    user_creds = await rq.get_user_credentials(message.from_user.id)
    if not user_creds:
        await message.reply("Пожалуйста, сначала авторизуйтесь с помощью команды /authorize")
        return

    await message.reply("Пожалуйста, отправьте фото, которое вы хотите загрузить.")
    await state.set_state(PhotoUploadState.waiting_for_photo)


async def photo_received(message: Message, state: FSMContext):
    if not message.photo:
        await message.reply("Пожалуйста, отправьте фото.")
        return

    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_path = file_info.file_path
    destination = f'{photo.file_id}.jpg'

    await message.bot.download_file(file_path, destination)
    await state.update_data(photo_path=destination)

    await message.reply("Фото получено. Теперь отправьте описание для фото.")
    await state.set_state(PhotoUploadState.waiting_for_description)


async def description_received(message: Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    photo_path = data['photo_path']

    response = await upload_photo(message.from_user.id, photo_path, description)
    os.remove(photo_path)
    logger.info(f"Фото {photo_path} удалено после загрузки")

    if response:
        await message.reply("Фото было успешно загружено.")
    else:
        await message.reply("Произошла ошибка при загрузке фото.")
        logger.error(f"Ошибка при загрузке фото {photo_path} для пользователя {message.from_user.id}")

    await state.clear()


async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.reply('Действие отменено.')


def register_photo_handlers(dp):
    dp.message.register(cancel_handler, commands="cancel", state="*")
