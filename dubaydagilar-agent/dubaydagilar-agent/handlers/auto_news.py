"""
Avtomatik yangilik tsikli.

cron-job.org kuniga 2 marta /trigger/morning va /trigger/evening
manzillariga so'rov yuboradi, shu modul ishga tushadi.

2-bosqich holati: yangiliklar Google News orqali yig'iladi, dublikatlar
filtrlanadi, sarlovha va havola bilan (hali tarjimasiz) kanalga joylanadi.

3-bosqichda: har bir yangilik uchun Gemini orqali qisqa xulosa va
tarjima qo'shiladi, format skrindagi ko'rinishga keltiriladi.
"""

import logging
from sources.news_gatherer import gather_fresh_news
from utils.telegram_api import post_to_channel
from utils.seen_links import mark_seen

logger = logging.getLogger("auto_news")

MAX_POSTS_PER_CYCLE = 6

CATEGORY_LABELS = {
    "turizm": "Turizm",
    "viza_rezidentlik": "Viza / Rezidentlik",
    "elchixona": "Elchixona",
    "jinoyat_xavfsizlik": "Xavfsizlik",
    "biznes_soliq": "Biznes / Soliq",
    "umumiy": "Umumiy",
}


def run_auto_news_cycle(slot):
    logger.info("Avtomatik tsikl ishga tushdi: %s", slot)

    fresh_items = gather_fresh_news()
    logger.info("Jami yangi element topildi: %d", len(fresh_items))

    if not fresh_items:
        logger.info("Yangi yangilik topilmadi, tsikl shu bilan tugaydi")
        return

    posted_count = 0
    for item in fresh_items:
        if posted_count >= MAX_POSTS_PER_CYCLE:
            break

        label = CATEGORY_LABELS.get(item["category"], item["category"])
        # TODO 3-bosqich: quyidagi qatorlar Gemini orqali tarjima/xulosa bilan almashtiriladi
        text = (
            f"<b>[{label}]</b>\n"
            f"{item['title']}\n\n"
            f"Manba: {item['source'] or 'nomalum'}\n"
            f"{item['link']}"
        )

        result = post_to_channel(text)
        if result.get("ok"):
            mark_seen(item["link"])
            posted_count += 1
        else:
            logger.error("Post qilishda xato: %s", result)

    logger.info("Tsikl tugadi. Postlangan: %d", posted_count)
