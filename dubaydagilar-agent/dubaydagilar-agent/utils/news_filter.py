"""
Yig'ilgan yangiliklarni sifat bo'yicha filtrlaydi.

Google News qidiruvi ba'zan reklama sahifalari, umumiy "About Us"
sahifalari yoki O'zbekistonga aloqasi yo'q umumiy yangiliklarni ham
qaytaradi. Bu modul har bir sarlovhani Gemini orqali tekshirib,
faqat haqiqatan foydali va aniq bo'lganlarini qoldiradi.

Agar filtr o'zi ishlamasa (Gemini xato bersa), xavfsiz tomonga —
hammasini qoldirishga — o'tadi, chunki bo'sh kanal filtri buzilgandan
ko'ra yomonroq.
"""

import logging
from utils.gemini_client import call_gemini, extract_json

logger = logging.getLogger("news_filter")

FILTER_CRITERIA = """Sen Dubaydagilar telegram kanali uchun yangiliklarni saralaydigan tahririyat yordamchisisan.
Faqat O'zbekiston fuqarolariga yoki BAA ga borish/yashashni rejalashtirgan odamlarga
haqiqatan foydali va qiziqarli bo'lgan yangiliklarni qoldirasan.

REJECT qilinadigan turdagi sarlovhalar:
- Umumiy "saytga tashrif buyuring", "batafsil ma'lumot uchun saytimizga kiring" kabi reklama/havola sahifalari
- "About Us", "General Information" kabi umumiy tashkilot sahifalari (aniq voqea/yangilik emas)
- Umumiy turizm reklamasi, aniq viza/qoida o'zgarishi bo'lmagan holda
- O'zbekiston bilan bog'liq bo'lmagan umumiy madaniy/tantanali tadbirlar (masalan YUNESKO ro'yxatiga kiritish)
- Umumiy lifestyle/restoran/dam olish reklamalari
- "Media" degan umumiy sahifa havolalari (masalan "Media - Dubai Police" — bu bosh sahifa, yangilik emas)
- Aniq raqam yoki foyda ko'rsatilmagan umumiy to'lov/siyosat sahifalari

KEEP qilinadigan turdagi sarlovhalar:
- O'zbekiston fuqarolariga tegishli aniq viza/rezidentlik o'zgarishlari (muddat uzaytirilishi, yangi talablar)
- Aniq soliq/tijorat o'zgarishlari (masalan korporativ soliq oshirilishi)
- Sayyohlar uchun amaliy moliyaviy imkoniyat (masalan aeroportda soliq qaytarish/cashback foizi)
- O'zbek fuqarolari ishtirok etgan aniq jinoyat yangiliklari (ushlanganlar, qutqarilganlar)
- Yirik xavfsizlik/texnologik yangiliklar (masalan yangi jinoyat aniqlash tizimi joriy etilishi)
- Elchixonaning aniq harakatlari (fuqarolarga yordam berish, qutqaruv, huquq himoyasi tadbiri) — umumiy "about" sahifalar emas
"""


def filter_relevant(items):
    """
    items: [{'category':..., 'title':..., 'link':..., 'source':...}, ...]
    Natija: faqat KEEP deb belgilangan elementlar ro'yxati
    """
    if not items:
        return items

    numbered_titles = "\n".join(f"{i+1}. {it['title']}" for i, it in enumerate(items))

    prompt = f"""{FILTER_CRITERIA}

Quyidagi sarlovhalarning har biri uchun aynan "KEEP" yoki "REJECT" deb belgila.

Sarlovhalar:
{numbered_titles}

Faqat quyidagi JSON formatda javob ber, boshqa hech narsa yozma:
{{"decisions": ["KEEP", "REJECT", "..."]}}

decisions ro'yxati aynan {len(items)} ta element bo'lishi, tartib saqlanishi shart."""

    try:
        raw = call_gemini(prompt, temperature=0.2)
        parsed = extract_json(raw)
        decisions = parsed.get("decisions", [])

        if len(decisions) != len(items):
            raise ValueError(f"Qarorlar soni mos kelmadi: {len(decisions)} vs {len(items)}")

        kept = [item for item, decision in zip(items, decisions) if decision.strip().upper() == "KEEP"]
        logger.info("Filtr natijasi: %d dan %d tasi qoldi", len(items), len(kept))
        return kept

    except Exception:
        logger.exception("Filtrda xato, xavfsizlik uchun barcha elementlar qoldiriladi")
        return items
