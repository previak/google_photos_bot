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
    try:
        user_creds = await rq.get_user_credentials(message.from_user.id)
        if not user_creds:
            await message.reply("Пожалуйста, сначала авторизуйтесь с помощью команды /authorize")
            return

        await message.reply("Пожалуйста, отправьте фото, которое вы хотите загрузить.")
        await state.set_state(PhotoUploadState.waiting_for_photo)
        logger.info(f"Пользователь {message.from_user.id} начал процесс загрузки фото.")
    except Exception as e:
        await message.reply("Произошла ошибка. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в start_photo_upload: {e}")


async def photo_received(message: Message, state: FSMContext):
    try:
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
        logger.info(f"Пользователь {message.from_user.id} отправил фото {destination}.")
    except Exception as e:
        await message.reply("Произошла ошибка при получении фото. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в photo_received: {e}")


async def description_received(message: Message, state: FSMContext):
    try:
        description = message.text
        data = await state.get_data()
        photo_path = data['photo_path']

        response = await upload_photo(message.from_user.id, photo_path, description)
        os.remove(photo_path)
        logger.info(f"Фото {photo_path} удалено после загрузки.")

        if response:
            await message.reply("Фото было успешно загружено.")
            logger.info(f"Фото {photo_path} успешно загружено для пользователя {message.from_user.id}.")
        else:
            await message.reply("Произошла ошибка при загрузке фото.")
            logger.error(f"Ошибка при загрузке фото {photo_path} для пользователя {message.from_user.id}.")

        await state.clear()
    except Exception as e:
        await message.reply("Произошла ошибка при загрузке фото. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в description_received: {e}")


async def cancel_handler(message: Message, state: FSMContext):
    try:
        await state.clear()
        await message.reply('Действие отменено.')
        logger.info(f"Пользователь {message.from_user.id} отменил действие.")
    except Exception as e:
        await message.reply("Произошла ошибка при отмене действия. Пожалуйста, попробуйте позже.")
        logger.error(f"Ошибка в cancel_handler: {e}")
