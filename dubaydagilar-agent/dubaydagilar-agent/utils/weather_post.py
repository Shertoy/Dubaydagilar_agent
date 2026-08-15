"""Ob-havo ma'lumotidan Gemini orqali post matni yaratadi."""

import logging
from utils.weather import get_dubai_weather
from utils.gemini_client import call_gemini
from utils.telegram_api import post_to_channel

logger = logging.getLogger("weather_post")


def create_and_post_weather():
    """
    Natija: (success: bool, message: str) — message admin'ga qaytariladigan tasdiq/xato matni
    """
    data = get_dubai_weather()
    if not data:
        return False, "Ob-havo ma'lumotini olishda xato yuz berdi. OPENWEATHER_API_KEY to'g'riligini tekshir."

    prompt = f"""Dubay shahri uchun bugungi ob-havo haqida qisqa (3-4 jumla), o'zbek tilida, jonli
va foydali Telegram posti yoz. Quyidagi ma'lumotlardan foydalan:

Harorat: {data['temp']} daraja
His qilinadigan harorat: {data['feels_like']} daraja
Tavsif: {data['description']}
Namlik: {data['humidity']} foiz
Shamol tezligi: {data['wind_speed']} m/s

Postda amaliy maslahat ham bo'lsin (masalan qanday kiyinish, suv ichish, quyoshdan himoyalanish).
Faqat post matnini yoz, boshqa hech narsa qo'shma, sarlovha yoki izoh yozma."""

    try:
        post_text = call_gemini(prompt).strip()
    except Exception:
        logger.exception("Gemini ob-havo postini yaratolmadi, oddiy formatga o'tamiz")
        post_text = (
            f"Bugun Dubayda harorat {data['temp']} daraja, "
            f"his qilinishi {data['feels_like']} daraja. "
            f"{data['description'].capitalize()}. Namlik {data['humidity']} foiz."
        )

    result = post_to_channel(f"<b>Bugungi ob-havo</b>\n\n{post_text}")

    if result.get("ok"):
        return True, "Ob-havo posti kanalga joylandi."
    else:
        logger.error("Ob-havo postini joylashda xato: %s", result)
        return False, "Post yaratildi, lekin kanalga joylashda xato yuz berdi."
