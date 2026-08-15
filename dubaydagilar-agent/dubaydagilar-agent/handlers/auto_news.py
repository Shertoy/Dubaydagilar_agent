"""
Avtomatik yangilik tsikli.

cron-job.org kuniga 2 marta /trigger/morning va /trigger/evening
manzillariga so'rov yuboradi, shu modul ishga tushadi.

3-bosqich holati: yig'ilgan yangiliklar Gemini orqali o'zbek tiliga
tarjima qilinadi, bitta jamlangan postga birlashtiriladi (har bir
sarlovha bosilsa manba sahifasiga olib boradi), kanalga bitta xabar
sifatida joylanadi.
"""

import logging
from sources.news_gatherer import gather_fresh_news, diversify_and_limit
from utils.news_translator import translate_items
from utils.post_formatter import build_digest_message
from utils.telegram_api import post_to_channel
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

    selected = diversify_and_limit(fresh_items, max_total=MAX_ITEMS_PER_DIGEST)
    logger.info("Postga tanlangan elementlar soni: %d", len(selected))

    intro, translated_items = translate_items(selected)
    message = build_digest_message(intro, translated_items)

    # Ko'p havola bo'lgani uchun avtomatik preview'ni o'chiramiz,
    # aks holda faqat bitta tasodifiy havola preview bo'lib chiqadi
    result = post_to_channel(message, disable_preview=True)

    if result.get("ok"):
        for item in translated_items:
            mark_seen(item["link"])
        logger.info("Jamlangan post muvaffaqiyatli joylandi: %d ta yangilik", len(translated_items))
    else:
        logger.error("Jamlangan postni joylashda xato: %s", result)
