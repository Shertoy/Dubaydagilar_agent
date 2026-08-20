"""
Bot narx (yoki boshqa ma'lumot) so'ragandan keyin, sen shunchaki javob
yozganingda ("5000 dirham" kabi), bot buni "tushunarsiz buyruq" deb
qabul qilmasligi uchun oldingi e'lon matnini vaqtincha eslab turadi.
"""

import json
import os
import threading
import logging

logger = logging.getLogger("pending_state")

STATE_FILE = "pending_state.json"
_lock = threading.Lock()


def get_pending_listing():
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("pending_listing")
    except (json.JSONDecodeError, IOError):
        return None


def set_pending_listing(text):
    with _lock:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"pending_listing": text}, f, ensure_ascii=False)


def clear_pending_listing():
    with _lock:
        if os.path.exists(STATE_FILE):
            try:
                os.remove(STATE_FILE)
            except IOError:
                pass
