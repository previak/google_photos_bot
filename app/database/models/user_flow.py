import json
from google_auth_oauthlib.flow import Flow
from sqlalchemy import BigInteger, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


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
