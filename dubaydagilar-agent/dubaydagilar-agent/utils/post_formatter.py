"""
Bitta jamlangan yangilik posti uchun matn tuzadi.

Format:
- Qalin sarlovha
- Gemini yaratgan kirish jumlasi
- Ketma-ket, guruhsiz ro'yxat: har bir sarlovha bosilsa manbaga o'tadi
"""


def build_digest_message(intro, items):
    """items har birida 'title_uz', 'link' bo'lishi kerak. Ketma-ket, guruhsiz ro'yxat."""

    lines = ["<b>BAAdagi qaynoq yangiliklar</b>", intro, ""]

    for it in items:
        title = it["title_uz"].strip()
        link = it["link"]
        lines.append(f"• <a href=\"{link}\">{title}</a>")

    return "\n".join(lines).strip()
