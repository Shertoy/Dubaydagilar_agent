"""Barcha kategoriyalar bo'yicha Google News'dan yangilik yig'adi va dublikatlarni tozalaydi."""

import logging
from sources.google_news import fetch_news
from sources.news_categories import CATEGORY_QUERIES, MAX_ITEMS_PER_CATEGORY
from utils.seen_links import filter_new

logger = logging.getLogger("news_gatherer")


def gather_fresh_news():
    """
    Har bir kategoriya bo'yicha yangilik qidiradi, hali postlanmaganlarini qaytaradi.
    Natija: [{'category':..., 'title':..., 'link':..., 'source':...}, ...]
    """
    fresh_items = []

    for category, queries in CATEGORY_QUERIES.items():
        category_links_seen_this_run = set()

        for query in queries:
            try:
                results = fetch_news(query, max_results=MAX_ITEMS_PER_CATEGORY)
            except Exception:
                logger.exception("Qidiruvda xato: %s / %s", category, query)
                continue

            new_links = filter_new([r["link"] for r in results])

            for r in results:
                if r["link"] not in new_links:
                    continue
                if r["link"] in category_links_seen_this_run:
                    continue
                category_links_seen_this_run.add(r["link"])
                fresh_items.append({
                    "category": category,
                    "title": r["title"],
                    "link": r["link"],
                    "source": r["source"],
                })

        logger.info("Kategoriya '%s': %d yangi element topildi", category, len(category_links_seen_this_run))

    return fresh_items


def diversify_and_limit(items, max_total=10):
    """
    Kategoriyalar orasidan navbat bilan (round-robin) tanlab, jami max_total
    tagacha element qaytaradi. Bitta kategoriya butun postni bosib olmasligi uchun.
    """
    by_category = {}
    for item in items:
        by_category.setdefault(item["category"], []).append(item)

    result = []
    while len(result) < max_total and any(by_category.values()):
        for category in list(by_category.keys()):
            if not by_category[category]:
                continue
            result.append(by_category[category].pop(0))
            if len(result) >= max_total:
                break

    return result
