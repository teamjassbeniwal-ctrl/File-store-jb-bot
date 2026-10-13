# utils/fsub_helper.py
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db


async def check_subscription(client, user_id, bot_key):
    """Return list of channels user has NOT joined."""
    status = await db.get_fsub_status(bot_key)
    if not status:
        return []

    channels = await db.get_force_channels(bot_key)
    not_joined = []
    for ch in channels:
        try:
            member = await client.get_chat_member(ch["id"], user_id)
            if member.status in ("left", "kicked", "banned"):
                not_joined.append(ch)
        except Exception:
            not_joined.append(ch)
    return not_joined


async def build_fsub_keyboard(client, bot_key, not_joined):
    """Build inline keyboard with Join buttons + I Joined."""
    buttons = []

    for ch in not_joined:
        try:
            chat = await client.get_chat(ch["id"])
            if ch.get("mode") == "request":
                invite = chat.invite_link or f"https://t.me/{chat.username}"
                label = f"📩 Request to Join {chat.title}"
            else:
                invite = chat.invite_link or f"https://t.me/{chat.username}"
                label = f"🔔 Join {chat.title}"
            buttons.append([InlineKeyboardButton(label, url=invite)])
        except Exception:
            pass

    buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="fsub_check")])
    return InlineKeyboardMarkup(buttons)
