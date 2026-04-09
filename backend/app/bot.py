import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHAT_ID = os.getenv("CHAT_ID", "")

def send_telegram_message(message: str) -> bool:
    """Send message to configured chat ID (for notifications)."""
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def send_telegram_message_direct(chat_id: str, message: str) -> bool:
    """Send message to specific chat ID (for direct notifications)."""
    if not BOT_TOKEN or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram direct error: {e}")
        return False

def setup_bot_commands():
    """Setup bot commands via Telegram API."""
    if not BOT_TOKEN:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    commands = [
        {"command": "start", "description": "Start the bot and link your account"},
        {"command": "mymatches", "description": "View your pending match requests"},
        {"command": "mygroups", "description": "View your study groups"},
        {"command": "accept", "description": "Accept a match request (usage: /accept <request_id>)"},
        {"command": "reject", "description": "Reject a match request (usage: /reject <request_id>)"},
        {"command": "help", "description": "Show help information"}
    ]
    
    payload = {"commands": commands}

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to setup bot commands: {e}")
        return False
