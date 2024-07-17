from aiogram.fsm.state import State, StatesGroup


class PhotoUploadState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_description = State()