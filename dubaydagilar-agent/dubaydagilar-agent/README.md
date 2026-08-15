# Dubaydagilar AI Agent — 1-bosqich (skelet)

## Nima tayyor

- Flask server, Render.com uchun tayyor
- Telegram webhook qabul qiladi, faqat sendan (ADMIN_USER_ID) kelgan xabarlarni qayta ishlaydi
- Kalit so'z asosida uch turdagi buyruqni ajratadi: ob-havo, e'lon, qo'llanma (hozircha stub javob qaytaradi)
- `/trigger/morning` va `/trigger/evening` — cron-job.org uchun tayyor manzillar (hozircha test post yuboradi)
- Barcha og'ir ishlar fon jarayonida (background thread) ishlaydi, Telegram/Render timeout bo'lmaydi

## Keyingi bosqichlar

- 2-bosqich: `sources/` papkasiga har bir manba uchun modul yoziladi (RSS o'qish, scraping)
- 3-bosqich: `utils/gemini_client.py` yaratiladi, xulosa/tarjima/sarlovha funksiyalari
- 4-bosqich: post formatlash funksiyasi (`utils/post_formatter.py`)
- 5-bosqich: `command_router.py` dagi stub funksiyalar to'liq ishlaydigan qilinadi
- 6-bosqich: cron-job.org sozlanadi
- 7-bosqich: xatoларни ушлаш va senga xabar yuborish kuchaytiriladi

## O'rnatish (Render.com)

1. Bu kodni GitHub repo'ga yukla
2. Render.com'da "New Web Service" yarat, repo'ni ulash
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Environment Variables bo'limiga qo'sh:
   - `TELEGRAM_BOT_TOKEN` — BotFather'dan olingan token
   - `ADMIN_USER_ID` — sening Telegram user ID'ing (bunga @userinfobot orqali qarash mumkin)
   - `CHANNEL_USERNAME` — masalan `@Dubaydagilar`
   - `GEMINI_API_KEY` — Google AI Studio'dan
   - `OPENWEATHER_API_KEY` — openweathermap.org'dan (keyingi bosqichda kerak bo'ladi)

## Webhook o'rnatish

Deploy tugagach, bir marta shu URL'ni brauzerda ochish kerak (TOKEN va RENDER_URL'ni o'zingnikiga almashtir):

```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=<RENDER_URL>/webhook/<TOKEN>
```

Masalan Render manzili `https://dubaydagilar-agent.onrender.com` bo'lsa:

```
https://api.telegram.org/bot123456:ABC-DEF/setWebhook?url=https://dubaydagilar-agent.onrender.com/webhook/123456:ABC-DEF
```

Muvaffaqiyatli bo'lsa `{"ok":true,"result":true,...}` javobi qaytadi.

## Test qilish

1. Bot'ga shaxsiy xabar yoz: "ob-havo haqida post qil"
2. Stub javobni olishing kerak: "Ob-havo posti tayyorlanmoqda..."
3. cron-job.org sozlashdan oldin `/trigger/morning` manzilini brauzerda qo'lda ochib ko'rish mumkin — kanalga test post kelishi kerak
