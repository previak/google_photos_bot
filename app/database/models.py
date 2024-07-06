import json
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from sqlalchemy import BigInteger, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import DB_URL

engine = create_async_engine(url=DB_URL)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True)
    tg_id = mapped_column(BigInteger)

    flows = relationship("UserFlow", back_populates="user")
    creds = relationship("UserCred", back_populates="user")


class UserFlow(Base):
    __tablename__ = 'user_flows'
    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'))
    state = mapped_column(Text)
    flow = mapped_column(Text)

    user = relationship("User", back_populates="flows")

    @property
    def flow_obj(self):
        flow_dict = json.loads(self.flow)
        client_config = flow_dict.get('client_config')
        scopes = flow_dict.get('scopes')
        redirect_uri = flow_dict.get('redirect_uri')

        flow = Flow.from_client_config(client_config, scopes)
        flow.redirect_uri = redirect_uri
        return flow

    @flow_obj.setter
    def flow_obj(self, flow: Flow):
        client_type = flow.client_type

        flow_dict = {
            'client_config': {client_type: flow.client_config},
            'scopes': flow.oauth2session.scope,
            'redirect_uri': flow.redirect_uri,
        }
        self.flow = json.dumps(flow_dict)


class UserCred(Base):
    __tablename__ = 'user_creds'
    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'))
    credentials = mapped_column(Text)

    user = relationship("User", back_populates="creds")

    @property
    def credentials_obj(self):
        cred_dict = json.loads(self.credentials)
        return self.dict_to_credentials(cred_dict)

    @credentials_obj.setter
    def credentials_obj(self, credentials):
        self.credentials = json.dumps(self.credentials_to_dict(credentials))

    @staticmethod
    def credentials_to_dict(credentials):
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes,
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }

    @staticmethod
    def dict_to_credentials(cred_dict):
        if cred_dict.get('expiry'):
            cred_dict['expiry'] = datetime.datetime.fromisoformat(cred_dict['expiry'])
        return Credentials(**cred_dict)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


