"""
Buyruq rejimi.

Sen botga shaxsiy xabar yozganingda shu modul ishga tushadi.
Hozircha oddiy kalit so'z asosida yo'naltiradi (1-bosqich skeleti).
3-bosqichda bu qism Gemini orqali "niyatni aniqlash" (intent detection)
bilan almashtiriladi, aniqroq ishlaydi.
"""

import logging
from utils.telegram_api import send_message

logger = logging.getLogger("command_router")

WEATHER_KEYWORDS = ["ob-havo", "ob havo", "havo"]
LISTING_KEYWORDS = ["ijaraga", "sotiladi", "sotaman", "xizmat"]
GUIDE_KEYWORDS = ["qo'llanma", "qollanma", "a dan z", "a-z"]


def route_command(chat_id, text, photo=None):
    text_lower = (text or "").lower()

    if not text and not photo:
        send_message(chat_id, "Xabar bo'sh keldi. Matn yoz.")
        return

    if any(kw in text_lower for kw in WEATHER_KEYWORDS):
        handle_weather_command(chat_id)
        return

    if any(kw in text_lower for kw in LISTING_KEYWORDS):
        handle_listing_command(chat_id, text, photo)
        return

    if any(kw in text_lower for kw in GUIDE_KEYWORDS):
        handle_guide_command(chat_id, text)
        return

    # Hech biriga to'g'ri kelmasa
    send_message(
        chat_id,
        "Buyruqni aniqlay olmadim. Quyidagilardan birini sina:\n"
        "- ob-havo haqida post qil\n"
        "- ijaraga/sotuvga oid e'lon matni yubor\n"
        "- biror mavzu bo'yicha A-Z qo'llanma yoz"
    )


def handle_weather_command(chat_id):
    # TODO 5-bosqich: utils/weather.py orqali OpenWeatherMap'dan ma'lumot olish
    # keyin Gemini orqali qisqa post matni yaratish va kanalga joylash
    send_message(chat_id, "Ob-havo posti tayyorlanmoqda (bu funksiya 5-bosqichda to'liq ishga tushadi).")
    logger.info("Weather command chaqirildi, hali stub")


def handle_listing_command(chat_id, text, photo):
    # TODO 5-bosqich: Gemini orqali matndan mavzu (ijara/sotuv/xizmat) va
    # kerakli maydonlarni (narx, manzil va h.k.) ajratib olish.
    # Yetarli bo'lsa post qilish, bo'lmasa nima yetishmayotganini so'rash.
    send_message(chat_id, "E'lon qabul qilindi, qayta ishlanmoqda (bu funksiya 5-bosqichda to'liq ishga tushadi).")
    logger.info("Listing command chaqirildi, hali stub. Rasm bormi: %s", bool(photo))


def handle_guide_command(chat_id, text):
    # TODO 5-bosqich: Gemini orqali to'liq qo'llanma matnini yaratish,
    # Telegraph API orqali sahifa qilib chop etish, kanalga qisqa post +
    # Telegraph havolasi bilan joylash.
    send_message(chat_id, "Qo'llanma tayyorlanmoqda (bu funksiya 5-bosqichda to'liq ishga tushadi).")
    logger.info("Guide command chaqirildi, hali stub")
