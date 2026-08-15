"""
Bitta jamlangan yangilik posti uchun matn tuzadi.

Format:
- Qalin sarlovha
- Gemini yaratgan kirish jumlasi
- Kategoriya bo'yicha guruhlangan, bosilsa manbaga o'tadigan sarlovhalar
"""

from utils.news_translator import CATEGORY_LABELS_UZ


def build_digest_message(intro, items):
    """items har birida 'title_uz', 'link', 'category' bo'lishi kerak."""

    lines = ["<b>BAAdagi qaynoq yangiliklar</b>", intro, ""]

    # Kategoriya bo'yicha guruhlash, faqat elementi bor kategoriyalar ko'rsatiladi
    grouped = {}
    for item in items:
        grouped.setdefault(item["category"], []).append(item)

    for category, cat_items in grouped.items():
        label = CATEGORY_LABELS_UZ.get(category, category)
        lines.append(f"<b>{label}</b>")
        for it in cat_items:
            title = it["title_uz"].strip()
            link = it["link"]
            lines.append(f"• <a href=\"{link}\">{title}</a>")
        lines.append("")

    return "\n".join(lines).strip()
