# Google Photos Bot

Google Photos Bot is a tool designed to interact with Google Photos. It helps in automating the upload of photos via a telegram bot interface.

## Features
- Upload photos to Google Photos.

## Getting Started

### Prerequisites
- Docker
- Docker Compose
- A Google Cloud project with the Google Photos API enabled
- A Telegram bot token from BotFather

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/previak/google_photos_bot.git
   cd google_photos_bot
   ```

2. **Google Cloud Setup**
   - Enable the Google Photos Library API in your Google Cloud project.
   - Create OAuth 2.0 credentials and download the client_secret.json file.
   - Place the `client_secret.json` file in the project root directory.
     
3. **Set up environment variables:**
   
   Create a `.env` file in the root directory with the following variables:
   ```plaintext
   TOKEN=your_token
   CLIENT_SECRETS_FILE=path_to_client_secrets.json
   SCOPES=your_scopes
   REDIRECT_URI=your_redirect_uri
   UPLOAD_URL=your_upload_url
   CREATE_URL=your_create_url
   DB_URL=your_database_url
   POSTGRES_USER=your_postgres_user
   POSTGRES_PASSWORD=your_postgres_password
   POSTGRES_DB=your_postgres_db
   ```
4. **Build and run the Docker containers:**
   ```bash
   docker-compose up -d
   ```

### Usage
Once the setup is complete, the bot should be up and running. You can interact with it according to your configuration and the provided functionalities.
