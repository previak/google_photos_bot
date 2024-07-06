import os
from google_auth_oauthlib.flow import Flow
import requests
from config import SCOPES, CLIENT_SECRETS_FILE, REDIRECT_URI, UPLOAD_URL, CREATE_URL
import app.database.requests as rq


async def get_authorization_url(tg_id):
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(prompt='consent',
                                                      access_type='offline',
                                                      include_granted_scopes='true')
    await rq.set_user_flow(tg_id, flow, state)
    return authorization_url


async def fetch_token(tg_id, state, code):
    flow, stored_state = await rq.get_user_flow_and_state(tg_id)
    if flow and stored_state == state:
        flow.fetch_token(code=code)
        await rq.set_user_cred(tg_id, flow.credentials)
        return True
    return False


async def upload_photo(tg_id, photo_path):
    creds = await rq.get_user_credentials(tg_id)
    if creds:
        headers = {
            'Authorization': f'Bearer {creds.token}',
            'Content-Type': 'application/octet-stream',
            'X-Goog-Upload-File-Name': os.path.basename(photo_path),
            'X-Goog-Upload-Protocol': 'raw',
        }

        with open(photo_path, 'rb') as photo_file:
            upload_response = requests.post(UPLOAD_URL, headers=headers, data=photo_file)

        if upload_response.status_code == 200:
            upload_token = upload_response.text

            create_body = {
                'newMediaItems': [
                    {
                        'description': 'Uploaded from Telegram',
                        'simpleMediaItem': {
                            'uploadToken': upload_token,
                        }
                    }
                ]
            }

            create_response = requests.post(CREATE_URL,
                                            headers={'Authorization': f'Bearer {creds.token}'}, json=create_body)

            if create_response.status_code == 200:
                return create_response.json()

    return None
