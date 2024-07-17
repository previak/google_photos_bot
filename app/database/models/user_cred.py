import json
import datetime
import logging
from google.oauth2.credentials import Credentials
from sqlalchemy import BigInteger, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserCred(Base):
    __tablename__ = 'user_creds'
    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[BigInteger] = mapped_column(ForeignKey('users.id'))
    credentials = mapped_column(Text)

    user = relationship("User", back_populates="creds")

    @property
    def credentials_obj(self):
        try:
            cred_dict = json.loads(self.credentials)
            return self.dict_to_credentials(cred_dict)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
            return None

    @credentials_obj.setter
    def credentials_obj(self, credentials):
        try:
            self.credentials = json.dumps(self.credentials_to_dict(credentials))
        except TypeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")

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
