import json
from app.database.models import async_session
from app.database.models import UserCred, UserFlow, User
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def set_user_flow(tg_id, flow, state):
    async with async_session() as session:
        user_query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(user_query)
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError(f"User with tg_id {tg_id} not found")

        new_flow = UserFlow(user_id=user.id, state=state)
        new_flow.flow_obj = flow
        session.add(new_flow)

        await session.commit()


async def set_user_cred(tg_id, cred):
    async with async_session() as session:
        user_query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(user_query)
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError(f"User with tg_id {tg_id} not found")

        cred_json = json.dumps(UserCred.credentials_to_dict(cred))
        new_creds = UserCred(user_id=user.id, credentials=cred_json)
        session.add(new_creds)

        await session.commit()


async def get_user_flow_and_state(tg_id):
    async with async_session() as session:
        user_query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(user_query)
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError(f"User with tg_id {tg_id} not found")

        flow_query = select(UserFlow).where(UserFlow.user_id == user.id).order_by(UserFlow.id.desc()).limit(1)
        result = await session.execute(flow_query)
        user_flow = result.scalar_one_or_none()

        if user_flow is None:
            raise ValueError(f"No flow found for user with tg_id {tg_id}")

        return user_flow.flow_obj, user_flow.state


async def get_user_credentials(tg_id):
    async with async_session() as session:
        user_query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(user_query)
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError(f"User with tg_id {tg_id} not found")

        cred_query = select(UserCred).where(UserCred.user_id == user.id)
        result = await session.execute(cred_query)
        user_cred = result.scalar_one_or_none()

        if user_cred is None:
            raise ValueError(f"No credentials found for user with tg_id {tg_id}")

        return user_cred.credentials_obj


async def get_user_flow_by_state(state):
    async with async_session() as session:
        flow_query = select(UserFlow).where(UserFlow.state == state).options(joinedload(UserFlow.user))
        result = await session.execute(flow_query)
        user_flow = result.scalar_one_or_none()

        return user_flow


async def get_tg_id_by_state(state):
    user_flow = await get_user_flow_by_state(state)

    if user_flow is None:
        raise ValueError("Invalid state")

    if not user_flow.user:
        raise ValueError("User not found")

    return user_flow.user.tg_id
