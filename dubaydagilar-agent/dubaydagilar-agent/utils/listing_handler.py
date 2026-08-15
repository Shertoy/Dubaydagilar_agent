"""
Sen yuborgan matnni (ijara, sotuv, xizmat taklifi) tahlil qilib,
tayyor post formatiga soladi. Faqat matn tahlil qilinadi, rasm tahlil qilinmaydi —
rasm bo'lsa, o'zgarishsiz postga biriktiriladi.
"""

import logging
from utils.gemini_client import call_gemini, extract_json

logger = logging.getLogger("listing_handler")


def analyze_listing(text):
    """
    Natija:
    {'status': 'ok', 'post_text': '...'} yoki
    {'status': 'missing', 'question': '...'}
    """
    prompt = f"""Sen Dubaydagilar telegram kanali uchun shaxsiy e'lonlarni post qilib beruvchi yordamchisan.

Foydalanuvchi quyidagi matnni yubordi, bu ijara, sotuv yoki xizmat taklifi bo'lishi mumkin:

"{text}"

Vazifang:
1. Mavzuni aniqla: ijara, sotuv, yoki xizmat.
2. Post uchun eng muhim maydon — narx. Agar narx ko'rsatilmagan bo'lsa, "missing" holatini qaytar.
3. Narx bor bo'lsa, matnni tozalab, chiroyli, o'qish oson Telegram post formatiga solib qayta yoz.
   HTML formatida <b>qalin</b> teglaridan foydalanib sarlovha va asosiy band(lar)ni ajratib ko'rsat.
   Emoji ishlatma. Matnni o'zgartirmasdan, faqat tartibga solib, kerak bo'lsa grammatikasini tuzatib yoz.

Faqat quyidagi JSON formatlardan BIRINI qaytar, boshqa hech narsa yozma:

Agar hammasi yetarli bo'lsa:
{{"status": "ok", "post_text": "tayyor post matni"}}

Agar narx yoki juda muhim ma'lumot yetishmasa:
{{"status": "missing", "question": "aniq nima yetishmayotganini so'ragan qisqa savol"}}"""

    try:
        raw = call_gemini(prompt)
        parsed = extract_json(raw)
        if parsed.get("status") not in ("ok", "missing"):
            raise ValueError("noto'g'ri status")
        return parsed
    except Exception:
        logger.exception("E'lonni tahlil qilishda xato")
        return {
            "status": "missing",
            "question": "E'loningni qayta ishlashda xato yuz berdi. Iltimos matnni qayta, biroz aniqroq yozib yubor (narxini albatta ko'rsat).",
        }
