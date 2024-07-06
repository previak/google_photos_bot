from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[BigInteger] = mapped_column(BigInteger, primary_key=True)
    tg_id = mapped_column(BigInteger)

    flows = relationship("UserFlow", back_populates="user")
    creds = relationship("UserCred", back_populates="user")
