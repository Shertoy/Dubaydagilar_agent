"""
Google Gemini API bilan ishlash.

Model nomlari Google tomonidan tez-tez o'zgartiriladi/o'chiriladi, shuning
uchun bir nechta nomni ketma-ket sinaymiz, birinchi ishlagani ishlatiladi.
"""

import json
import logging
import re
import requests
from config import GEMINI_API_KEY

logger = logging.getLogger("gemini_client")

# Eng yangisidan eskisiga qarab sinaladi
CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
]

API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"


def call_gemini(prompt, temperature=0.7):
    """
    Berilgan prompt uchun Gemini'dan matn javob oladi.
    Barcha modellar ishlamasa, RuntimeError chiqaradi.
    """
    last_error = None

    for model in CANDIDATE_MODELS:
        url = API_URL_TEMPLATE.format(model=model, key=GEMINI_API_KEY)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code != 200:
                last_error = f"{model}: HTTP {resp.status_code} - {resp.text[:200]}"
                logger.warning("Gemini model ishlamadi (%s), keyingisiga o'tamiz", model)
                continue

            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text

        except (KeyError, IndexError, requests.RequestException) as e:
            last_error = f"{model}: {e}"
            logger.warning("Gemini model xato berdi (%s): %s", model, e)
            continue

    raise RuntimeError(f"Barcha Gemini modellari ishlamadi. Oxirgi xato: {last_error}")


def extract_json(text):
    """Gemini javobidan JSON qismini ajratib oladi (```json fenslarni tozalaydi)."""
    cleaned = re.sub(r"```json|```", "", text).strip()
    return json.loads(cleaned)
