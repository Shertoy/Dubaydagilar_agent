"""
Bitta jamlangan yangilik posti uchun matn tuzadi.

Format:
- Qalin sarlovha
- Gemini yaratgan kirish jumlasi
- Ketma-ket, guruhsiz ro'yxat: har bir sarlovha bosilsa manbaga o'tadi
"""

from utils.html_utils import escape_html


def build_digest_message(intro, items):
    """items har birida 'title_uz', 'link' bo'lishi kerak. Ketma-ket, guruhsiz ro'yxat."""

    lines = ["<b>BAAdagi qaynoq yangiliklar</b>", escape_html(intro), ""]

    for it in items:
        title = escape_html(it["title_uz"].strip())
        link = escape_html(it["link"])
        lines.append(f"• <a href=\"{link}\">{title}</a>")

    return "\n".join(lines).strip()
