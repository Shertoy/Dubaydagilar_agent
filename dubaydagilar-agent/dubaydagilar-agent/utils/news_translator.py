"""
Yig'ilgan yangilik sarlovhalarini o'zbek tiliga tarjima qiladi va
post uchun qisqa, jonli kirish jumlasi yaratadi.
"""

import logging
from utils.gemini_client import call_gemini, extract_json

logger = logging.getLogger("news_translator")

CATEGORY_LABELS_UZ = {
    "turizm": "Turizm",
    "viza_rezidentlik": "Viza va rezidentlik",
    "elchixona": "Elchixona",
    "jinoyat_xavfsizlik": "Xavfsizlik",
    "biznes_soliq": "Biznes va soliq",
    "umumiy": "Umumiy yangiliklar",
}


def translate_items(items):
    """
    items: [{'category':..., 'title':..., 'link':..., 'source':...}, ...]
    Natija: (intro_text, items) — items'ga 'title_uz' maydoni qo'shilgan holda
    """
    if not items:
        return "", items

    numbered_titles = "\n".join(
        f"{i+1}. [{CATEGORY_LABELS_UZ.get(it['category'], it['category'])}] {it['title']}"
        for i, it in enumerate(items)
    )

    prompt = f"""Sen Dubaydagilar telegram kanali uchun yangiliklar tayyorlaysan.

Quyida BAA (Dubay) haqidagi yangilik sarlovhalari ingliz tilida berilgan, raqamlangan.

Vazifang:
1. Har bir sarlovhani tabiiy, ravon o'zbek tiliga tarjima qil. So'zma-so'z emas, o'zbekcha gapirilgandek tushunarli va qisqa qil.
2. Yangiliklar to'plami uchun bitta qisqa (10-15 so'z), jonli, qiziqarli kirish jumlasi yoz. Masalan "BAAda bugun nima gap?" kabi ohangda, lekin har safar boshqacha va tabiiy yozilgan bo'lsin.

Sarlovhalar:
{numbered_titles}

Faqat quyidagi JSON formatda javob ber, boshqa hech qanday matn, izoh yoki fens (```) qo'shma:
{{"intro": "kirish jumlasi", "titles": ["1-tarjima", "2-tarjima", "..."]}}

titles ro'yxati aynan {len(items)} ta element bo'lishi, tartib saqlanishi shart."""

    try:
        raw = call_gemini(prompt)
        parsed = extract_json(raw)
        translated_titles = parsed.get("titles", [])
        intro = parsed.get("intro", "BAAdagi so'nggi yangiliklar")

        if len(translated_titles) != len(items):
            raise ValueError(f"Tarjima soni mos kelmadi: {len(translated_titles)} vs {len(items)}")

        for item, title_uz in zip(items, translated_titles):
            item["title_uz"] = title_uz

        return intro, items

    except Exception:
        logger.exception("Tarjimada xato, inglizcha sarlovhalar bilan davom etamiz")
        for item in items:
            item["title_uz"] = item["title"]  # zaxira: tarjimasiz asl matn
        return "BAAdagi so'nggi yangiliklar", items
