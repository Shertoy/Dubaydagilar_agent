"""
Postlangan havolalarni saqlash (dedup).

Oddiy JSON fayl ishlatamiz, chunki hajm katta emas (bir necha ming havola).
Fayl Render'ning disk fazosida saqlanadi. DIQQAT: Render'ning bepul rejasida
disk doimiy emas, deploy qilinganda tozalanishi mumkin. Agar shu muammo
chiqsa, keyinroq bepul bazaga (masalan Supabase) o'tkazamiz.
"""

import json
import os
import logging
from config import SEEN_LINKS_DB_PATH

logger = logging.getLogger("seen_links")

MAX_STORED_LINKS = 2000  # fayl cheksiz o'smasligi uchun


def _load():
    if not os.path.exists(SEEN_LINKS_DB_PATH):
        return []
    try:
        with open(SEEN_LINKS_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        logger.warning("seen_links faylini o'qib bo'lmadi, bo'sh ro'yxatdan boshlanadi")
        return []


def _save(links):
    with open(SEEN_LINKS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(links[-MAX_STORED_LINKS:], f)


def is_seen(link):
    return link in _load()


def mark_seen(link):
    links = _load()
    if link not in links:
        links.append(link)
        _save(links)


def filter_new(links):
    """Berilgan ro'yxatdan faqat hali postlanmagan havolalarni qaytaradi."""
    seen = set(_load())
    return [link for link in links if link not in seen]
