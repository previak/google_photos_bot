import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import requests
from config import SCOPES, CLIENT_SECRETS_FILE, REDIRECT_URI, UPLOAD_URL, CREATE_URL

user_flows = {}
user_creds = {}

def get_authorization_url(user_id):
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    user_flows[user_id] = (flow, state)
    return authorization_url

def fetch_token(user_id, state, code):
    flow, stored_state = user_flows.get(user_id, (None, None))
    if flow and stored_state == state:
        flow.fetch_token(code=code)
        user_creds[user_id] = flow.credentials
        return True
    return False

def upload_photo(user_id, photo_path):
    creds = user_creds.get(user_id)
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

            create_response = requests.post(CREATE_URL, headers={'Authorization': f'Bearer {creds.token}'}, json=create_body)

            if create_response.status_code == 200:
                return create_response.json()

    return None
