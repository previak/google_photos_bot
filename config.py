TOKEN = '7295243161:AAGWTrBnFzFI7PC4LigQBneuTWU6UA89pkk'
CLIENT_SECRETS_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.sharing']
REDIRECT_URI = 'http://localhost:8000/callback'
UPLOAD_URL = 'https://photoslibrary.googleapis.com/v1/uploads'
CREATE_URL = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'
DB_URL = 'postgresql+asyncpg://postgres:postgres@localhost/google_photos_db'
