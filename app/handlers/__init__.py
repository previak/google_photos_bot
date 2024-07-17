from aiogram import Router
from aiogram.filters import Command, CommandStart

from .common import start_handler, authorize_handler, code_handler, process_code, AuthState
from .photo import start_photo_upload, photo_received, description_received, cancel_handler, PhotoUploadState

router = Router()

router.message.register(start_handler, CommandStart())
router.message.register(authorize_handler, Command('authorize'))
router.message.register(code_handler, Command('code'))
router.message.register(process_code, AuthState.waiting_for_code)
router.message.register(start_photo_upload, Command('photo'))
router.message.register(photo_received, PhotoUploadState.waiting_for_photo)
router.message.register(description_received, PhotoUploadState.waiting_for_description)
router.message.register(cancel_handler, Command('cancel'))
