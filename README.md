# Telegram Video Downloader Bot

A Telegram bot for downloading videos from various platforms including TikTok, Instagram Reels, and YouTube Shorts.

## Features

- **Download Videos from TikTok**
- **Download Videos from Instagram Reels**
- **Download Videos from YouTube Shorts**
- **Cache Previously Downloaded Videos**
- **Chat Authorization System**

## Installation

Follow these steps to set up the Telegram Video Downloader Bot locally.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/telegram-video-downloader.git
cd telegram-video-downloader
```

### 2. Create a Virtual Environment and Install Dependencies

```bash
python -m venv venv
```

Activate the virtual environment:

- **For Linux/Mac:**

    ```bash
    source venv/bin/activate
    ```

- **For Windows:**

    ```bash
    venv\Scripts\activate
    ```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the `config` directory and populate it with your credentials:

```env
BOT_TOKEN=your_bot_token
AUTH_CHAT_ID=your_auth_chat_id

# Instagram Credentials (You can use one set; obtainable via browser developer tools)
USER_AGENT=your_user_agent
X_IG_APP_ID=your_ig_app_id
COOKIES=your_cookies

```

## Usage

1. **Start the Bot:**

    ```bash
    python main.py
    ```

2. **Authorize the Bot in a Chat:**

    - Add the bot to your desired chat.
    - Send the command `/auth` to authorize.

3. **Download a Video:**

    - Send the video link to the chat with the bot.
    - The bot will download and provide the video.

## License

This project is licensed under the [MIT License](LICENSE).