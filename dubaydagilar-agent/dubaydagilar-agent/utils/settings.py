"""
Bot sozlamalarini saqlash va o'qish.

Sen botga "sozlama emoji yoqilsin" yoki "sozlama emoji ochirilsin" deb
yozsang, shu yerga saqlanadi va keyingi barcha postlarda ishlatiladi.
Fayl asosida ishlaydi, oddiy va tushunarli.
"""

import json
import os
import logging

logger = logging.getLogger("settings")

SETTINGS_FILE = "bot_settings.json"

DEFAULT_SETTINGS = {
    "emoji_enabled": True,
}


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        return merged
    except (json.JSONDecodeError, IOError):
        logger.warning("Sozlamalar faylini o'qib bo'lmadi, standart qiymatlar ishlatiladi")
        return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return settings


def get_setting(key):
    return load_settings().get(key, DEFAULT_SETTINGS.get(key))
