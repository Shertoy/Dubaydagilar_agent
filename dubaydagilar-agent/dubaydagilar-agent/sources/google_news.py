"""
Google News RSS orqali yangilik qidirish.

Har bir sayt uchun alohida RSS manzil izlash o'rniga, Google News'ning
tayyor qidiruv-RSS xizmatidan foydalanamiz. Bu yondashuv afzalligi:
- Yuzlab manbani birlashtirib beradi
- Bironta sayt dizaynini o'zgartirsa ham bizning kodimiz buzilmaydi
- Har doim eng so'nggi va tegishli natijalarni beradi

Manzil formati:
https://news.google.com/rss/search?q=QIDIRUV&hl=en-US&gl=AE&ceid=AE:en
"""

import logging
import feedparser
import requests
from urllib.parse import quote

logger = logging.getLogger("google_news")

BASE_URL = "https://news.google.com/rss/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_news(query, max_results=8):
    """
    query: qidiruv so'zi, masalan 'UAE visa OR residency'
    Natija: [{'title':..., 'link':..., 'published':..., 'source':...}, ...]
    """
    encoded_query = quote(query)
    url = f"{BASE_URL}?q={encoded_query}&hl=en-US&gl=AE&ceid=AE:en"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.warning("Google News so'rovida xato: %s (query: %s)", e, query)
        return []

    feed = feedparser.parse(resp.content)

    if feed.bozo and not feed.entries:
        logger.warning("Google News RSS o'qishda muammo: %s (query: %s)", feed.bozo_exception, query)
        return []

    results = []
    for entry in feed.entries[:max_results]:
        results.append({
            "title": entry.get("title", "").strip(),
            "link": entry.get("link", "").strip(),
            "published": entry.get("published", ""),
            "source": entry.get("source", {}).get("title", "") if entry.get("source") else "",
        })
    return results
