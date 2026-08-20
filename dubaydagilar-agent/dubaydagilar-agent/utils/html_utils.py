"""
Telegram HTML formatiga matn qo'shishdan oldin xavfsiz qilish.

Yangilik sarlovhalari yoki havolalarda "&", "<", ">" kabi belgilar
bo'lsa, Telegram'ning HTML formatini buzadi va butun post
jo'natilmay qoladi. Shu funksiya shunday belgilarni xavfsiz
ko'rinishga o'tkazadi.
"""

import html


def escape_html(text):
    """Matnni Telegram HTML formatiga xavfsiz qo'shish uchun tayyorlaydi."""
    return html.escape(text or "", quote=True)
