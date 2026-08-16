"""
Yangiliklarni bitta bosqichda filtrlaydi va tarjima qiladi.

Oldin bu ikki alohida Gemini so'rovi edi (avval filtr, keyin tarjima).
Bu so'rovlar sonini ikki baravar oshirar, ba'zan Google'ning daqiqalik
limitiga tegib, ba'zi sarlovhalar tarjimasiz qolib ketardi.

Endi bitta so'rovda ikkalasi ham bajariladi: har bir sarlovha uchun
"kerakmi (BAA bilan bog'liqmi, foydalimi)" va "tarjimasi" birga
qaytariladi. Bu deyarli ikki barobar kamroq so'rov degani.
"""

import logging
import time
from utils.gemini_client import call_gemini, extract_json

logger = logging.getLogger("news_processor")

DEFAULT_INTRO = "BAAdagi so'nggi yangiliklar"

CRITERIA = """Sen Dubaydagilar telegram kanali uchun yangiliklarni saralaydigan va tarjima qiluvchi tahririyat yordamchisisan.
Kanal O'ZBEKISTON fuqarolariga va BAA (Dubay)ga borish/yashashni rejalashtirgan odamlarga mo'ljallangan.

REJECT qilinadigan sarlovhalar (aynan shu mezonlarga qara):
- BAA bilan HECH QANDAY aloqasi yo'q, faqat boshqa davlat haqida (masalan Saudiya Arabistoni, Ummon, Qatar — BAA tilga olinmasa)
- Faqat O'zbekiston ICHIDA sodir bo'lgan, BAA bilan aloqasi yo'q voqealar (masalan Toshkentdagi jinoyat, agar BAA bilan bog'liq bo'lmasa)
- Umumiy "saytga tashrif buyuring", reklama, "About Us" kabi sahifalar
- O'zbekiston bilan bog'liq bo'lmagan umumiy BAA madaniy/tantanali tadbirlari
- Umumiy lifestyle/restoran reklamalari, "Media" umumiy sahifalari
- Aniq foyda/raqam ko'rsatilmagan umumiy siyosat sahifalari

KEEP qilinadigan sarlovhalar (IKKALASI ham to'g'ri kelishi shart: aniq/foydali VA BAA bilan bog'liq):
- O'zbekiston fuqarolariga tegishli aniq BAA viza/rezidentlik o'zgarishlari
- BAA dagi aniq soliq/tijorat o'zgarishlari
- Sayyohlar uchun BAA da amaliy moliyaviy imkoniyat (masalan aeroportda soliq qaytarish)
- O'zbek fuqarolari BAA da ishtirok etgan aniq jinoyat/sud yangiliklari
- BAA dagi yirik xavfsizlik/texnologik yangiliklar
- O'zbekiston elchixonasining BAA dagi aniq harakatlari (fuqarolarga yordam, qutqaruv)
- BAA-O'zbekiston rasmiy aloqalari (rahbarlar muloqoti, bitimlar, hamkorlik)
"""


def process_items(items):
    """
    items: [{'title':..., 'link':..., 'category':...}, ...]
    Natija: (intro, kept_items_with_title_uz, failed_count)
    """
    if not items:
        return DEFAULT_INTRO, [], 0

    intro, kept, success = _try_batch_process(items)
    if success:
        return intro, kept, 0

    logger.warning("Ommaviy jarayon ishlamadi, har birini alohida, pauza bilan qayta ishlaymiz")
    return _process_one_by_one(items)


def _try_batch_process(items):
    numbered = "\n".join(f"{i+1}. {it['title']}" for i, it in enumerate(items))

    prompt = f"""{CRITERIA}

Sarlovhalar:
{numbered}

Har bir sarlovha uchun qaror qil va agar KEEP bo'lsa, o'zbek tiliga tabiiy, ravon tarjima qil.
Tarjima matnida qo'shtirnoq (") ishlatma, o'rniga oddiy tirnoq (') ishlat.

Yana bitta umumiy, jonli (10-15 so'zli) kirish jumlasi yoz.

Faqat quyidagi JSON formatda javob ber, boshqa hech narsa yozma:
{{
  "intro": "kirish jumlasi",
  "items": [
    {{"keep": true, "title_uz": "tarjima"}},
    {{"keep": false, "title_uz": ""}}
  ]
}}

items ro'yxati aynan {len(items)} ta element bo'lishi, tartib saqlanishi shart."""

    try:
        raw = call_gemini(prompt, temperature=0.3)
        parsed = extract_json(raw)
        decisions = parsed.get("items", [])
        intro = parsed.get("intro", DEFAULT_INTRO)

        if len(decisions) != len(items):
            raise ValueError(f"Qarorlar soni mos kelmadi: {len(decisions)} vs {len(items)}")

        kept = []
        for item, decision in zip(items, decisions):
            if decision.get("keep"):
                item["title_uz"] = decision.get("title_uz") or item["title"]
                kept.append(item)

        logger.info("Ommaviy jarayon: %d dan %d tasi qoldi", len(items), len(kept))
        return intro, kept, True

    except Exception:
        logger.exception("Ommaviy jarayonda xato")
        return DEFAULT_INTRO, [], False


def _process_one_by_one(items):
    """
    Har birini alohida qayta ishlaydi. Har chaqiruv orasida pauza qo'yiladi,
    aks holda Gemini'ning daqiqalik so'rov limitiga tegib qolish xavfi bor.
    """
    kept = []
    failed_count = 0

    for idx, item in enumerate(items):
        if idx > 0:
            time.sleep(1.5)

        decision = _process_single(item["title"])
        if decision is None:
            # Gemini bu bitta element uchun ham ishlamadi.
            # Xavfsizlik uchun qoldiramiz (yo'qotmaslik yaxshiroq), lekin belgilab qo'yamiz.
            item["title_uz"] = item["title"]
            kept.append(item)
            failed_count += 1
            continue

        if decision.get("keep"):
            item["title_uz"] = decision.get("title_uz") or item["title"]
            kept.append(item)

    return DEFAULT_INTRO, kept, failed_count


def _process_single(title):
    prompt = f"""{CRITERIA}

Sarlovha: {title}

Shu bitta sarlovha uchun qaror qil. Faqat quyidagi JSON formatda javob ber, boshqa hech narsa yozma:
{{"keep": true yoki false, "title_uz": "agar keep true bo'lsa o'zbekcha tarjima, aks holda bo'sh qoldir"}}"""

    try:
        raw = call_gemini(prompt, temperature=0.3)
        return extract_json(raw)
    except Exception:
        logger.exception("Yakka qayta ishlashda xato: %s", title)
        return None
