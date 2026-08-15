"""
Avtomatik yangilik tsikli.

cron-job.org kuniga 2 marta /trigger/morning va /trigger/evening
manzillariga so'rov yuboradi, shu modul ishga tushadi.

Hozircha skelet (1-bosqich). 2-bosqichda sources/ papkasidagi
manba modullaridan yangi havolalar yig'iladi, 3-bosqichda
Gemini orqali xulosa/tarjima qilinadi, 4-bosqichda formatlab
kanalga joylanadi.
"""

import logging
from utils.telegram_api import post_to_channel

logger = logging.getLogger("auto_news")


def run_auto_news_cycle(slot):
    logger.info("Avtomatik tsikl ishga tushdi: %s", slot)

    # TODO 2-bosqich: sources/ papkasidagi har bir manbadan yangi
    # havolalarni yig'ish, seen_links.json bilan solishtirib
    # faqat yangilarini qoldirish

    # TODO 3-bosqich: har bir yangi havola uchun to'liq matnni o'qib,
    # Gemini orqali xulosa + sarlovha + tarjima yaratish

    # TODO 4-bosqich: formatlab kanalga joylash (post_to_channel orqali)

    # Hozircha faqat tsikl ishlaganini tasdiqlash uchun test post
    post_to_channel(f"[TEST] Avtomatik tsikl ishladi: {slot}. Bu xabar 2-bosqichda haqiqiy yangilik bilan almashtiriladi.")
