from google_auth_oauthlib.flow import Flow

import app.database.requests as rq
from config import SCOPES, CLIENT_SECRETS_FILE, REDIRECT_URI


async def get_authorization_url(tg_id):
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    await rq.set_user_flow(tg_id, flow, state)
    return authorization_url


async def fetch_token(tg_id, state, code):
    flow, stored_state = await rq.get_user_flow_and_state(tg_id)
    if flow and stored_state == state:
        flow.fetch_token(code=code)
        await rq.set_user_cred(tg_id, flow.credentials)
        return True
    return False
