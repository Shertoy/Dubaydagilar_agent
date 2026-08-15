"""To'liq A-Z qo'llanma yaratadi (Gemini), Telegraph'da chop etadi, kanalga qisqa post joylaydi."""

import logging
from utils.gemini_client import call_gemini, extract_json
from utils.telegraph_client import publish_guide
from utils.telegram_api import post_to_channel

logger = logging.getLogger("guide_handler")


def generate_and_publish_guide(topic_text):
    """
    Natija: (success: bool, message: str) — admin'ga qaytariladigan tasdiq/xato matni
    """
    prompt = f"""Sen Dubaydagilar telegram kanali uchun to'liq, batafsil A dan Z gacha qo'llanma yozuvchisan.

Foydalanuvchi so'ragan mavzu: "{topic_text}"

Vazifang: shu mavzu bo'yicha o'zbek tilida, aniq, amaliy, qadam-baqadam to'liq qo'llanma yoz.
Rasmiy BAA qonunchiligiga mos, aniq va foydali bo'lsin. Umumiy gaplardan qoch, real amaliy
qadamlarni yoz.

Faqat quyidagi JSON formatda javob ber, boshqa hech narsa yozma:

{{
  "title": "qo'llanma sarlovhasi (qisqa)",
  "channel_intro": "kanalga qo'yiladigan 2-3 jumlali qiziqarli kirish matni",
  "sections": [
    {{"heading": "bo'lim sarlovhasi", "body": "bo'lim matni, kerak bo'lsa bir necha paragraf, \\n\\n bilan ajratilgan"}},
    ...
  ]
}}

Kamida 4, ko'pi bilan 8 ta bo'lim bo'lsin."""

    try:
        raw = call_gemini(prompt, temperature=0.6)
        parsed = extract_json(raw)
        title = parsed["title"]
        channel_intro = parsed["channel_intro"]
        sections = parsed["sections"]
    except Exception:
        logger.exception("Qo'llanma matnini yaratishda xato")
        return False, "Qo'llanma matnini yaratishda xato yuz berdi. Mavzuni biroz aniqroq yozib qayta yubor."

    try:
        page_url = publish_guide(title, sections)
    except Exception:
        logger.exception("Telegraph sahifasini yaratishda xato")
        return False, "Qo'llanma matni tayyor bo'ldi, lekin Telegraph sahifasini yaratishda xato yuz berdi."

    channel_message = (
        f"<b>{title}</b>\n\n"
        f"{channel_intro}\n\n"
        f"To'liq qo'llanma: {page_url}"
    )

    result = post_to_channel(channel_message)

    if result.get("ok"):
        return True, f"Qo'llanma kanalga joylandi.\nTo'liq sahifa: {page_url}"
    else:
        logger.error("Qo'llanma postini kanalga joylashda xato: %s", result)
        return False, f"Telegraph sahifasi tayyor ({page_url}), lekin kanalga joylashda xato yuz berdi."
