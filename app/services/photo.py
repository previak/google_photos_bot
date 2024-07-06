import os
import requests

import app.database.requests as rq
from config import UPLOAD_URL, CREATE_URL


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
