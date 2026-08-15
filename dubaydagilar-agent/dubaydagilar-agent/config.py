"""
Barcha maxfiy kalitlar va sozlamalar shu yerdan o'qiladi.
Render.com'da Environment Variables bo'limiga qo'shiladi, kodga yozilmaydi.
"""

import os

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@Dubaydagilar")
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID", "")  # sening Telegram user ID'ing

# AI
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Ob-havo
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
DUBAI_LAT = 25.2048
DUBAI_LON = 55.2708

# Telegraph (A-Z qo'llanmalar uchun)
TELEGRAPH_AUTHOR_NAME = os.environ.get("TELEGRAPH_AUTHOR_NAME", "Dubaydagilar")
TELEGRAPH_ACCESS_TOKEN = os.environ.get("TELEGRAPH_ACCESS_TOKEN", "")  # bo'sh bo'lsa, ishga tushganda avtomatik yaratiladi

# Baza fayli (postlangan havolalarni saqlash uchun, dedup)
SEEN_LINKS_DB_PATH = os.environ.get("SEEN_LINKS_DB_PATH", "seen_links.json")

REQUIRED_VARS = ["TELEGRAM_BOT_TOKEN", "ADMIN_USER_ID", "GEMINI_API_KEY"]


def validate_config():
    missing = [name for name in REQUIRED_VARS if not globals().get(name)]
    if missing:
        raise RuntimeError(f"Quyidagi muhit o'zgaruvchilari yetishmayapti: {', '.join(missing)}")
