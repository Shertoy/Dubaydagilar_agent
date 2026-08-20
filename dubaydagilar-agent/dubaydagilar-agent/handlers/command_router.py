"""
Buyruq rejimi.

Sen botga shaxsiy xabar yozganingda shu modul ishga tushadi.
Kalit so'z asosida turdagi buyruqni ajratadi: sozlama, ob-havo, shaxsiy
e'lon, A-Z qo'llanma.

Agar bot e'lon uchun narx (yoki boshqa ma'lumot) so'rab, sen shunchaki
javob yozsang ("5000 dirham" kabi, hech qanday kalit so'zsiz), bot buni
oldingi e'lonning davomi deb tushunadi — alohida "tushunmadim" javobi
bermaydi.
"""

import logging
from utils.telegram_api import send_message, post_to_channel, post_photo_to_channel
from utils.weather_post import create_and_post_weather
from utils.listing_handler import analyze_listing
from utils.guide_handler import generate_and_publish_guide
from utils.settings import set_setting
from utils.pending_state import get_pending_listing, set_pending_listing, clear_pending_listing

logger = logging.getLogger("command_router")

SETTINGS_KEYWORDS = ["sozlama"]
WEATHER_KEYWORDS = ["ob-havo", "ob havo", "obhavo"]
LISTING_KEYWORDS = ["ijaraga", "sotiladi", "sotaman", "sotuv", "xizmat"]
GUIDE_KEYWORDS = ["qo'llanma", "qollanma", "a dan z", "a-z", "qanday ochish", "talablari"]


def route_command(chat_id, text, photo=None):
    text_lower = (text or "").lower()

    if not text and not photo:
        send_message(chat_id, "Xabar bo'sh keldi. Matn yoz.")
        return

    if any(kw in text_lower for kw in SETTINGS_KEYWORDS):
        handle_settings_command(chat_id, text_lower)
        return

    if any(kw in text_lower for kw in WEATHER_KEYWORDS):
        clear_pending_listing()
        handle_weather_command(chat_id)
        return

    if any(kw in text_lower for kw in LISTING_KEYWORDS):
        # Bu yangi e'lon, eskisini unutamiz
        handle_listing_command(chat_id, text, photo)
        return

    if any(kw in text_lower for kw in GUIDE_KEYWORDS):
        clear_pending_listing()
        handle_guide_command(chat_id, text)
        return

    # Hech qanday kalit so'z topilmadi — bu oldingi e'lonning davomi bo'lishi mumkin
    pending = get_pending_listing()
    if pending:
        combined_text = f"{pending}\n{text}"
        handle_listing_command(chat_id, combined_text, photo)
        return

    send_message(
        chat_id,
        "Buyruqni aniqlay olmadim. Quyidagilardan birini sina:\n"
        "- ob-havo haqida post qil\n"
        "- ijaraga/sotuvga oid e'lon matni yubor\n"
        "- biror mavzu bo'yicha A-Z qo'llanma yoz\n"
        "- sozlama emoji yoqilsin / sozlama emoji ochirilsin"
    )


def handle_settings_command(chat_id, text_lower):
    if "emoji" in text_lower:
        if any(w in text_lower for w in ["ochir", "off", "kerak emas"]):
            set_setting("emoji_enabled", False)
            send_message(chat_id, "Emoji o'chirildi. Endi postlarda emoji ishlatilmaydi.")
        elif any(w in text_lower for w in ["yoq", "on", "kerak"]):
            set_setting("emoji_enabled", True)
            send_message(chat_id, "Emoji yoqildi. Endi postlarda mos joylarda emoji ishlatiladi.")
        else:
            send_message(chat_id, "Tushunmadim. 'sozlama emoji yoqilsin' yoki 'sozlama emoji ochirilsin' deb yoz.")
        return

    send_message(
        chat_id,
        "Hozircha faqat emoji sozlamasi bor.\n"
        "'sozlama emoji yoqilsin' yoki 'sozlama emoji ochirilsin' deb yoz."
    )


def handle_weather_command(chat_id):
    send_message(chat_id, "Ob-havo posti tayyorlanmoqda...")
    success, message = create_and_post_weather()
    send_message(chat_id, message)


def handle_listing_command(chat_id, text, photo):
    send_message(chat_id, "E'lon qayta ishlanmoqda...")
    result = analyze_listing(text)

    if result["status"] == "missing":
        set_pending_listing(text)
        send_message(chat_id, result["question"])
        return

    clear_pending_listing()
    post_text = result["post_text"]

    if photo:
        file_id = photo[-1]["file_id"]
        tg_result = post_photo_to_channel(file_id, caption=post_text)
    else:
        tg_result = post_to_channel(post_text)

    if tg_result.get("ok"):
        send_message(chat_id, "E'lon kanalga joylandi.")
    else:
        logger.error("E'lonni kanalga joylashda xato: %s", tg_result)
        send_message(chat_id, "E'lon tayyor bo'ldi, lekin kanalga joylashda xato yuz berdi.")


def handle_guide_command(chat_id, text):
    send_message(chat_id, "Qo'llanma tayyorlanmoqda, bu biroz vaqt olishi mumkin...")
    success, message = generate_and_publish_guide(text)
    send_message(chat_id, message)
