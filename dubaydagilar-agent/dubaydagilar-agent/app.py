"""
Dubaydagilar AI Agent - asosiy server

Ikki vazifani bajaradi:
1. Telegram'dan kelgan shaxsiy xabarlarni qabul qilib, buyruq rejimini ishga tushiradi
2. cron-job.org'dan kelgan /trigger so'rovlarini qabul qilib, avtomatik yangilik yig'ish/post qilish jarayonini boshlaydi
"""

import os
import logging
import threading
from flask import Flask, request, jsonify

from config import ADMIN_USER_ID, TELEGRAM_BOT_TOKEN
from utils.telegram_api import send_message, answer_webhook_ok
from handlers.command_router import route_command
from handlers.auto_news import run_auto_news_cycle

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

app = Flask(__name__)


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "dubaydagilar-agent"}), 200


@app.route(f"/webhook/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    """Telegram bot'ga yozilgan har bir xabar shu yerga keladi."""
    update = request.get_json(silent=True) or {}
    logger.info("Webhook update olindi: %s", update.get("update_id"))

    message = update.get("message")
    if not message:
        return answer_webhook_ok()

    chat_id = message.get("chat", {}).get("id")
    user_id = message.get("from", {}).get("id")
    text = message.get("text", "")
    photo = message.get("photo")

    # Faqat admin (loyiha egasi) bilan ishlaymiz
    if str(user_id) != str(ADMIN_USER_ID):
        logger.warning("Notanish foydalanuvchidan xabar: %s", user_id)
        return answer_webhook_ok()

    # Og'ir ishni fon jarayoniga o'tkazamiz, Telegram'ga darhol javob qaytaramiz
    # (Render/Cloudflare timeout muammosining oldini olish uchun)
    thread = threading.Thread(
        target=handle_admin_message_safe,
        args=(chat_id, text, photo),
    )
    thread.start()

    return answer_webhook_ok()


def handle_admin_message_safe(chat_id, text, photo):
    """route_command'ni xato ushlab chaqiradi, fon jarayonida ishlaydi."""
    try:
        route_command(chat_id=chat_id, text=text, photo=photo)
    except Exception:
        logger.exception("Buyruqni qayta ishlashda xato")
        send_message(chat_id, "Xabaringni qayta ishlashda xato yuz berdi. Qayta urinib ko'r.")


@app.route("/trigger/<slot>", methods=["GET", "POST"])
def trigger_auto_cycle(slot):
    """
    cron-job.org shu manzilga so'rov yuboradi.
    slot: 'morning' yoki 'evening'
    """
    if slot not in ("morning", "evening"):
        return jsonify({"error": "noto'g'ri slot"}), 400

    logger.info("Avtomatik tsikl boshlandi: %s", slot)

    thread = threading.Thread(target=run_auto_news_cycle_safe, args=(slot,))
    thread.start()

    return jsonify({"status": "started", "slot": slot}), 200


def run_auto_news_cycle_safe(slot):
    try:
        run_auto_news_cycle(slot)
    except Exception:
        logger.exception("Avtomatik tsiklda xato: %s", slot)
        send_message(ADMIN_USER_ID, f"{slot} tsiklida xato yuz berdi. Loglarni tekshir.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
