import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_FILE')
SCOPES = os.getenv('SCOPES').split(',')
REDIRECT_URI = os.getenv('REDIRECT_URI')
UPLOAD_URL = os.getenv('UPLOAD_URL')
CREATE_URL = os.getenv('CREATE_URL')
DB_URL = os.getenv('DB_URL')
