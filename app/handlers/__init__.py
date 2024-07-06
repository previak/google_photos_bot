from aiogram import Router
from aiogram.filters import Command, CommandStart

from .common import start_handler, authorize_handler
from .photo import photo_handler


router = Router()

router.message.register(start_handler, CommandStart())
router.message.register(authorize_handler, Command('authorize'))
router.message.register(photo_handler, Command('photo'))
