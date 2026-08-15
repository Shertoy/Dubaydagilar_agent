"""
Telegraph (telegra.ph) bilan ishlash.

Uzun qo'llanmalar uchun alohida sahifa yaratadi, kanalga esa qisqa
post + shu sahifaning havolasi joylanadi.

Access token bir marta yaratiladi va faylga saqlanadi (Render disk
o'chib qolsa qayta yaratiladi, muammo emas).
"""

import json
import logging
import os
import requests
from config import TELEGRAPH_AUTHOR_NAME, TELEGRAPH_ACCESS_TOKEN

logger = logging.getLogger("telegraph_client")

TOKEN_FILE = "telegraph_token.json"
API_BASE = "https://api.telegra.ph"


def _get_access_token():
    if TELEGRAPH_ACCESS_TOKEN:
        return TELEGRAPH_ACCESS_TOKEN

    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)["access_token"]
        except (json.JSONDecodeError, KeyError, IOError):
            pass

    # Yangi hisob yaratamiz
    resp = requests.post(f"{API_BASE}/createAccount", json={
        "short_name": TELEGRAPH_AUTHOR_NAME,
        "author_name": TELEGRAPH_AUTHOR_NAME,
    }, timeout=15)
    resp.raise_for_status()
    result = resp.json()["result"]
    token = result["access_token"]

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump({"access_token": token}, f)

    logger.info("Yangi Telegraph hisobi yaratildi")
    return token


def _text_to_nodes(sections):
    """
    sections: [{'heading':..., 'body':...}, ...]
    Telegraph Node formatiga o'giradi.
    """
    nodes = []
    for section in sections:
        if section.get("heading"):
            nodes.append({"tag": "h3", "children": [section["heading"]]})
        body = section.get("body", "")
        for paragraph in body.split("\n\n"):
            paragraph = paragraph.strip()
            if paragraph:
                nodes.append({"tag": "p", "children": [paragraph]})
    return nodes


def publish_guide(title, sections, author_name=None):
    """
    title: sahifa sarlovhasi
    sections: [{'heading':..., 'body':...}, ...]
    Natija: sahifa URL manzili
    """
    token = _get_access_token()
    nodes = _text_to_nodes(sections)

    resp = requests.post(f"{API_BASE}/createPage", json={
        "access_token": token,
        "title": title,
        "author_name": author_name or TELEGRAPH_AUTHOR_NAME,
        "content": nodes,
        "return_content": False,
    }, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("ok"):
        raise RuntimeError(f"Telegraph sahifa yaratilmadi: {data}")

    return data["result"]["url"]
