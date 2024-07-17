import json
import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.database.models.base import async_session
from app.database.models.user import User
from app.database.models.user_cred import UserCred
from app.database.models.user_flow import UserFlow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_user_by_tg_id(tg_id):
    async with async_session() as session:
        user_query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(user_query)
        return result.scalar_one_or_none()


async def set_user(tg_id):
    try:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))

            if not user:
                session.add(User(tg_id=tg_id))
                await session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        raise


async def set_user_flow(tg_id, flow, state):
    try:
        async with async_session() as session:
            user = await get_user_by_tg_id(tg_id)

            if user is None:
                raise ValueError(f"User with tg_id {tg_id} not found")

            new_flow = UserFlow(user_id=user.id, state=state)
            new_flow.flow_obj = flow
            session.add(new_flow)

            await session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении потока пользователя: {e}")
        raise


async def set_user_cred(tg_id, cred):
    try:
        async with async_session() as session:
            user = await get_user_by_tg_id(tg_id)

            if user is None:
                raise ValueError(f"User with tg_id {tg_id} not found")

            cred_json = json.dumps(UserCred.credentials_to_dict(cred))
            new_creds = UserCred(user_id=user.id, credentials=cred_json)
            session.add(new_creds)

            await session.commit()
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении учетных данных пользователя: {e}")
        raise


async def get_user_flow_and_state(tg_id):
    try:
        async with async_session() as session:
            user = await get_user_by_tg_id(tg_id)

            if user is None:
                raise ValueError(f"User with tg_id {tg_id} not found")

            flow_query = select(UserFlow).where(UserFlow.user_id == user.id).order_by(UserFlow.id.desc()).limit(1)
            result = await session.execute(flow_query)
            user_flow = result.scalar_one_or_none()

            if user_flow is None:
                raise ValueError(f"No flow found for user with tg_id {tg_id}")

            return user_flow.flow_obj, user_flow.state
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении потока и состояния пользователя: {e}")
        raise


async def get_user_credentials(tg_id):
    try:
        async with async_session() as session:
            user = await get_user_by_tg_id(tg_id)

            if user is None:
                raise ValueError(f"User with tg_id {tg_id} not found")

            cred_query = select(UserCred).where(UserCred.user_id == user.id).order_by(UserCred.id.desc()).limit(1)
            result = await session.execute(cred_query)
            user_cred = result.scalar_one_or_none()

            if user_cred is None:
                raise ValueError(f"No credentials found for user with tg_id {tg_id}")

            return user_cred.credentials_obj
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении учетных данных пользователя: {e}")
        raise


async def get_user_flow_by_state(state):
    try:
        async with async_session() as session:
            flow_query = select(UserFlow).where(UserFlow.state == state).options(joinedload(UserFlow.user))
            result = await session.execute(flow_query)
            user_flow = result.scalar_one_or_none()

            return user_flow
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении потока по состоянию: {e}")
        raise


async def get_tg_id_by_state(state):
    try:
        user_flow = await get_user_flow_by_state(state)

        if user_flow is None:
            raise ValueError("Invalid state")

        if not user_flow.user:
            raise ValueError("User not found")

        return user_flow.user.tg_id
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении tg_id по состоянию: {e}")
        raise
