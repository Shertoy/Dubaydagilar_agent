"""
Har bir mavzu (kategoriya) uchun Google News qidiruv so'zlari.

Qidiruvlar ataylab tor va aniq qilib tanlangan: umumiy "Dubay turizmi"
kabi keng mavzular emas, balki O'zbekiston fuqarolariga yoki BAA ga
borish/yashashni rejalashtirgan odamlarga bevosita tegishli narsalar.

Topilgan natijalar keyin utils/news_filter.py orqali яна bir marta
sifat filtridan o'tadi (reklama, umumiy "about" sahifalar chiqarib
tashlanadi).
"""

CATEGORY_QUERIES = {
    "viza_rezidentlik": [
        "Uzbekistan citizens UAE visa",
        "O'zbekiston fuqarolari BAA viza",
        "UAE tourist visa extension Uzbekistan",
        "site:gdrfad.gov.ae Uzbekistan",
    ],
    "moliya_xarid": [
        "UAE tax refund tourists airport",
        "Dubai VAT refund cashback shopping",
        "UAE corporate tax increase business",
    ],
    "elchixona": [
        "Uzbekistan embassy UAE citizens help",
        "O'zbekiston elchixonasi BAA fuqaro",
        "Uzbekistan consulate UAE rescue OR repatriation",
    ],
    "xavfsizlik": [
        "Uzbek national arrested Dubai",
        "O'zbek jinoyatchi BAA ushlandi",
        "Dubai police new crime detection technology",
        "UAE human trafficking arrest Uzbekistan",
    ],
    "biznes_soliq": [
        "UAE corporate tax business news",
        "UAE free zone business setup update",
        "site:mof.gov.ae UAE tax",
    ],
    "umumiy": [
        "UAE new law policy change",
        "site:wam.ae Uzbekistan",
    ],
}

# Har bir so'rovdan nechta natija olishning yuqori chegarasi
MAX_ITEMS_PER_CATEGORY = 3
