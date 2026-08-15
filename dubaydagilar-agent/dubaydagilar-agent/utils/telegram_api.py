"""Telegram Bot API bilan ishlash uchun oddiy wrapper funksiyalar."""

import logging
import requests
from flask import jsonify

from config import TELEGRAM_BOT_TOKEN, CHANNEL_USERNAME

logger = logging.getLogger("telegram_api")

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Telegram'ning rasm ostidagi yozuv (caption) uchun belgilar chegarasi
CAPTION_LIMIT = 1024


def send_message(chat_id, text, disable_preview=False, parse_mode="HTML"):
    """Berilgan chat_id'ga (shaxsiy yoki kanal) matn xabar yuboradi."""
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_preview,
    }
    resp = requests.post(url, json=payload, timeout=15)
    if not resp.ok:
        logger.error("sendMessage xato: %s", resp.text)
    return resp.json()


def send_photo(chat_id, photo_file_id_or_url, caption="", parse_mode="HTML"):
    """
    Rasm bilan xabar yuboradi. photo_file_id_or_url Telegram file_id yoki tashqi URL bo'lishi mumkin.
    Agar caption 1024 belgidan uzun bo'lsa, rasm ostiga qisqartirilgan matn qo'yiladi,
    to'liq matn esa alohida xabar sifatida ketidan yuboriladi (hech narsa yo'qolmaydi).
    """
    url = f"{BASE_URL}/sendPhoto"

    caption_to_send = caption
    needs_followup = False
    if len(caption) > CAPTION_LIMIT:
        caption_to_send = caption[: CAPTION_LIMIT - 20].rstrip() + "... (davomi quyida)"
        needs_followup = True

    payload = {
        "chat_id": chat_id,
        "photo": photo_file_id_or_url,
        "caption": caption_to_send,
        "parse_mode": parse_mode,
    }
    resp = requests.post(url, json=payload, timeout=30)
    if not resp.ok:
        logger.error("sendPhoto xato: %s", resp.text)

    if needs_followup and resp.ok:
        send_message(chat_id, caption)

    return resp.json()


def post_to_channel(text, disable_preview=False):
    """Kanalga matn post qiladi."""
    return send_message(CHANNEL_USERNAME, text, disable_preview=disable_preview)


def post_photo_to_channel(photo_file_id_or_url, caption=""):
    """Kanalga rasm bilan post qiladi."""
    return send_photo(CHANNEL_USERNAME, photo_file_id_or_url, caption=caption)


def set_webhook(webhook_url):
    """Bot webhook manzilini o'rnatadi. Deploy qilingandan keyin bir marta chaqiriladi."""
    url = f"{BASE_URL}/setWebhook"
    resp = requests.post(url, json={"url": webhook_url}, timeout=15)
    return resp.json()


def answer_webhook_ok():
    """Telegram'ga darhol 200 OK qaytarish uchun."""
    return jsonify({"ok": True}), 200
