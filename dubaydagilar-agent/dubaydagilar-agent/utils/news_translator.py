"""
Yig'ilgan yangilik sarlovhalarini o'zbek tiliga tarjima qiladi va
post uchun qisqa, jonli kirish jumlasi yaratadi.

Ikki bosqichli usul:
1. Avval barcha sarlovhalarni bitta so'rovda tarjima qilishga urinadi (tez).
2. Agar bu ishlamasa (masalan JSON buzilib qolsa), har bir sarlovhani
   alohida-alohida tarjima qiladi (sekinroq, lekin ancha barqaror —
   bitta sarlovhadagi xato boshqalariga ta'sir qilmaydi).

Shu tufayli post har doim o'zbek tilida chiqadi, faqat juda kam holatda
(masalan Gemini butunlay ishlamay qolsa) inglizcha qoladi.
"""

import logging
from utils.gemini_client import call_gemini, extract_json

logger = logging.getLogger("news_translator")

CATEGORY_LABELS_UZ = {
    "viza_rezidentlik": "Viza va rezidentlik",
    "moliya_xarid": "Moliya va xarid",
    "elchixona": "Elchixona",
    "xavfsizlik": "Xavfsizlik",
    "biznes_soliq": "Biznes va soliq",
    "umumiy": "Umumiy yangiliklar",
}

DEFAULT_INTRO = "BAAdagi so'nggi yangiliklar"


def translate_items(items):
    """
    items: [{'category':..., 'title':..., 'link':..., 'source':...}, ...]
    Natija: (intro_text, items, failed_count)
    - items'ga 'title_uz' maydoni qo'shilgan holda qaytariladi
    - failed_count: nechta sarlovha tarjima qilinolmay, asl ingliz holida qolgani
    """
    if not items:
        return "", items, 0

    intro, success = _try_batch_translate(items)
    if success:
        return intro, items, 0

    logger.warning("Ommaviy tarjima ishlamadi, har bir sarlovhani alohida tarjima qilamiz")
    failed_count = _translate_one_by_one(items)
    return DEFAULT_INTRO, items, failed_count


def _try_batch_translate(items):
    """Barcha sarlovhalarni bitta so'rovda tarjima qilishga urinadi. Muvaffaqiyat bo'lsa (intro, True)."""
    numbered_titles = "\n".join(
        f"{i+1}. [{CATEGORY_LABELS_UZ.get(it['category'], it['category'])}] {it['title']}"
        for i, it in enumerate(items)
    )

    prompt = f"""Sen Dubaydagilar telegram kanali uchun yangiliklar tayyorlaysan.

Quyida BAA (Dubay) haqidagi yangilik sarlovhalari ingliz tilida berilgan, raqamlangan.

Vazifang:
1. Har bir sarlovhani tabiiy, ravon o'zbek tiliga tarjima qil. So'zma-so'z emas, o'zbekcha gapirilgandek tushunarli va qisqa qil.
2. Yangiliklar to'plami uchun bitta qisqa (10-15 so'z), jonli, qiziqarli kirish jumlasi yoz.

Sarlovhalar:
{numbered_titles}

Faqat quyidagi JSON formatda javob ber, boshqa hech qanday matn, izoh yoki fens (```) qo'shma.
Tarjima matni ichida qo'shtirnoq (") belgisidan foydalanma, buning o'rniga oddiy tirnoq (') ishlat:
{{"intro": "kirish jumlasi", "titles": ["1-tarjima", "2-tarjima", "..."]}}

titles ro'yxati aynan {len(items)} ta element bo'lishi, tartib saqlanishi shart."""

    try:
        raw = call_gemini(prompt)
        parsed = extract_json(raw)
        translated_titles = parsed.get("titles", [])
        intro = parsed.get("intro", DEFAULT_INTRO)

        if len(translated_titles) != len(items):
            raise ValueError(f"Tarjima soni mos kelmadi: {len(translated_titles)} vs {len(items)}")

        for item, title_uz in zip(items, translated_titles):
            item["title_uz"] = title_uz

        return intro, True

    except Exception:
        logger.exception("Ommaviy tarjimada xato")
        return DEFAULT_INTRO, False


def _translate_one_by_one(items):
    """Har bir sarlovhani alohida tarjima qiladi. Natija: nechta sarlovha muvaffaqiyatsiz bo'lgani."""
    failed_count = 0
    for item in items:
        translated = _translate_single_title(item["title"])
        item["title_uz"] = translated
        if translated == item["title"]:
            failed_count += 1
    return failed_count


def _translate_single_title(title):
    """Bitta sarlovhani tarjima qiladi. Xato bo'lsa, asl matnni qaytaradi."""
    prompt = (
        "Quyidagi ingliz tilidagi yangilik sarlovhasini tabiiy, ravon o'zbek tiliga tarjima qil. "
        "Faqat tarjima matnini yoz, tirnoq belgisi, izoh yoki boshqa hech narsa qo'shma.\n\n"
        f"Sarlovha: {title}"
    )
    try:
        result = call_gemini(prompt, temperature=0.3).strip()
        result = result.strip('"').strip("'").strip()
        return result if result else title
    except Exception:
        logger.exception("Yakka tarjimada xato: %s", title)
        return title
