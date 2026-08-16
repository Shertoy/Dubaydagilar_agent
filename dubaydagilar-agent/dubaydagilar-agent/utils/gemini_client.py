"""
Google Gemini API bilan ishlash.

Ikki narsa navbat bilan sinaladi va eslab qolinadi:
1. API kalit (agar GEMINI_API_KEY_2 berilgan bo'lsa, birinchisi limitga
   tegganda ikkinchisiga o'tiladi)
2. Model nomi (Google tez-tez o'zgartiradi/o'chiradi, shuning uchun
   bir nechtasi ketma-ket sinaladi)

Oxirgi ishlagan kombinatsiya (kalit + model) eslab qolinadi, keyingi
safar birinchi shu sinaladi — tezroq va kamroq xato.

429 (so'rov limiti) xatosi alohida ushlanadi: bir marta qisqa kutib
qayta urinib ko'riladi, ishlamasa keyingi kombinatsiyaga o'tiladi.
"""

import json
import logging
import re
import time
import requests
from config import GEMINI_API_KEY, GEMINI_API_KEY_2

logger = logging.getLogger("gemini_client")

CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
]

# Faqat bo'sh bo'lmagan kalitlar ishlatiladi
API_KEYS = [k for k in [GEMINI_API_KEY, GEMINI_API_KEY_2] if k]

API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

# Oxirgi ishlagan kombinatsiya
_last_working = {"key_index": 0, "model": None}


def _ordered_key_indices():
    """Oxirgi ishlagan kalit indeksini ro'yxat boshiga chiqaradi."""
    idx = _last_working["key_index"]
    indices = list(range(len(API_KEYS)))
    if idx in indices:
        return [idx] + [i for i in indices if i != idx]
    return indices


def _ordered_models():
    """Oxirgi ishlagan modelni ro'yxat boshiga chiqaradi."""
    model = _last_working["model"]
    if model and model in CANDIDATE_MODELS:
        return [model] + [m for m in CANDIDATE_MODELS if m != model]
    return CANDIDATE_MODELS


def call_gemini(prompt, temperature=0.7):
    """
    Berilgan prompt uchun Gemini'dan matn javob oladi.
    Barcha kalit+model kombinatsiyalari ishlamasa, RuntimeError chiqaradi.
    """
    global _last_working

    if not API_KEYS:
        raise RuntimeError("Hech qanday Gemini API kalit topilmadi (GEMINI_API_KEY bo'sh)")

    last_error = None

    for key_index in _ordered_key_indices():
        key = API_KEYS[key_index]

        for model in _ordered_models():
            url = API_URL_TEMPLATE.format(model=model, key=key)
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": temperature},
            }

            for attempt in range(2):  # 429 bo'lsa bir marta qayta urinamiz
                try:
                    resp = requests.post(url, json=payload, timeout=30)

                    if resp.status_code == 429:
                        last_error = f"kalit#{key_index+1}/{model}: HTTP 429 (so'rov limiti)"
                        if attempt == 0:
                            logger.warning("Gemini limiti (kalit#%d, %s), 3 soniya kutamiz", key_index + 1, model)
                            time.sleep(3)
                            continue
                        else:
                            logger.warning("Gemini limiti hali ham, keyingi kombinatsiyaga o'tamiz")
                            break

                    if resp.status_code != 200:
                        last_error = f"kalit#{key_index+1}/{model}: HTTP {resp.status_code} - {resp.text[:200]}"
                        logger.warning("Gemini ishlamadi (kalit#%d, %s), keyingisiga o'tamiz", key_index + 1, model)
                        break

                    data = resp.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    _last_working = {"key_index": key_index, "model": model}
                    return text

                except (KeyError, IndexError, requests.RequestException) as e:
                    last_error = f"kalit#{key_index+1}/{model}: {e}"
                    logger.warning("Gemini xato berdi (kalit#%d, %s): %s", key_index + 1, model, e)
                    break

    raise RuntimeError(f"Barcha Gemini kombinatsiyalari ishlamadi. Oxirgi xato: {last_error}")


def extract_json(text):
    """Gemini javobidan JSON qismini ajratib oladi (```json fenslarni tozalaydi)."""
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)
