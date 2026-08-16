"""
Avtomatik yangilik tsikli.

cron-job.org kuniga 2 marta /trigger/morning va /trigger/evening
manzillariga so'rov yuboradi, shu modul ishga tushadi.

Yig'ilgan yangiliklar bitta bosqichda (utils/news_processor.py) filtrlanadi
va tarjima qilinadi, bitta jamlangan postga birlashtiriladi, kanalga
joylanadi. Agar ba'zi sarlovhalar qayta ishlanmasa, admin'ga xabar beriladi.
"""

import logging
from config import ADMIN_USER_ID
from sources.news_gatherer import gather_fresh_news, diversify_and_limit
from utils.news_processor import process_items
from utils.post_formatter import build_digest_message
from utils.telegram_api import post_to_channel, send_message
from utils.seen_links import mark_seen

logger = logging.getLogger("auto_news")

MAX_ITEMS_PER_DIGEST = 10


def run_auto_news_cycle(slot):
    logger.info("Avtomatik tsikl ishga tushdi: %s", slot)

    fresh_items = gather_fresh_news()
    logger.info("Jami yangi element topildi: %d", len(fresh_items))

    if not fresh_items:
        logger.info("Yangi yangilik topilmadi, tsikl shu bilan tugaydi")
        return

    intro, processed_items, failed_count = process_items(fresh_items)
    logger.info("Qayta ishlangandan keyin qoldi: %d", len(processed_items))

    if not processed_items:
        logger.info("Filtrdan keyin hech narsa qolmadi, tsikl shu bilan tugaydi")
        return

    selected = diversify_and_limit(processed_items, max_total=MAX_ITEMS_PER_DIGEST)
    logger.info("Postga tanlangan elementlar soni: %d", len(selected))

    message = build_digest_message(intro, selected)
    result = post_to_channel(message, disable_preview=True)

    if result.get("ok"):
        for item in selected:
            mark_seen(item["link"])
        logger.info("Jamlangan post muvaffaqiyatli joylandi: %d ta yangilik", len(selected))

        if failed_count > 0:
            send_message(
                ADMIN_USER_ID,
                f"Diqqat: {slot} postida {failed_count} ta sarlovha to'liq qayta ishlanmadi "
                f"(tarjimasiz qolgan bo'lishi mumkin). Odatda bu Gemini limiti tugaganda yuz beradi."
            )
    else:
        logger.error("Jamlangan postni joylashda xato: %s", result)
