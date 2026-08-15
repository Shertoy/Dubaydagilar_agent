"""
Har bir mavzu (kategoriya) uchun Google News qidiruv so'zlari.

Har bir kategoriyada bir nechta qidiruv bor:
- Rasmiy manbaga qaratilgan (site:...) qidiruv, eng ishonchli natija beradi
- Umumiy kalit so'z qidiruvi, kengroq qamrov uchun
"""

CATEGORY_QUERIES = {
    "turizm": [
        "site:visitdubai.com",
        "site:mediaoffice.ae tourism",
        "Dubai new attraction OR resort OR beach club opening",
    ],
    "viza_rezidentlik": [
        "site:gdrfad.gov.ae",
        "site:u.ae visa",
        "UAE visa rule change OR golden visa OR residency",
    ],
    "elchixona": [
        "site:uzembassy.ae",
    ],
    "jinoyat_xavfsizlik": [
        "site:dubaipolice.gov.ae",
        "Dubai crime OR fraud OR scam warning",
    ],
    "biznes_soliq": [
        "site:dubaichamber.com",
        "site:mof.gov.ae UAE tax",
        "UAE corporate tax OR business setup OR free zone",
    ],
    "umumiy": [
        "site:wam.ae",
        "Dubai news today",
    ],
}

# Har bir kategoriyadan bir tsiklda nechta yangilik olishning yuqori chegarasi
MAX_ITEMS_PER_CATEGORY = 3
