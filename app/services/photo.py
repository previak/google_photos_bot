import os
import requests
import logging
import app.database.requests as rq
from config import UPLOAD_URL, CREATE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def upload_photo(tg_id, photo_path, description):
    try:
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
                            'description': description,
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
                else:
                    logger.error(f"Ошибка при создании медиа-элемента в Google Photos: {create_response.status_code}")
            else:
                logger.error(f"Ошибка при загрузке фото на сервер Google Photos: {upload_response.status_code}")

    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке фото в Google Photos: {e}")

    return None
