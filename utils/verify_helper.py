# utils/verify_helper.py
import time
from database import db


def parse_time(time_str):
    """Convert '15m' or '2h' to seconds."""
    try:
        if time_str.endswith("m"):
            return int(time_str[:-1]) * 60
        if time_str.endswith("h"):
            return int(time_str[:-1]) * 3600
        return 120
    except Exception:
        return 120


async def needs_verification(user_id, bot_key):
    """True if user must verify before downloading."""
    status = await db.get_verify_status(bot_key)
    if not status:
        return False  # verification disabled

    last = await db.get_user_verify_time(user_id, bot_key)
    if not last:
        return True

    wait_seconds = parse_time(await db.get_verify_time(bot_key))
    return (time.time() - last) >= wait_seconds


async def mark_verified(user_id, bot_key):
    await db.set_user_verify_time(user_id, bot_key, time.time())
