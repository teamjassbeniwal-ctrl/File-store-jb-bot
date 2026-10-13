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
            status_str = str(member.status).split(".")[-1].lower()
            if status_str in ("left", "kicked", "banned"):
                not_joined.append(ch)
        except Exception as e:
            print(f"FSub check error for {ch['id']}: {e}")
            not_joined.append(ch)
    return not_joined


async def build_fsub_keyboard(client, bot_key, not_joined):
    """Build inline keyboard with Join/Request buttons + I Joined."""
    buttons = []

    for ch in not_joined:
        try:
            chat = await client.get_chat(ch["id"])
            mode = ch.get("mode", "normal")

            # Build the invite link
            invite = None

            # Try to export a fresh invite link
            try:
                invite = await client.export_chat_invite_link(ch["id"])
            except Exception as e:
                print(f"Export invite error: {e}")

            # Fallback to chat.username (public channels)
            if not invite:
                invite = f"https://t.me/{chat.username}" if chat.username else None

            # Final fallback to stored invite
            if not invite and chat.invite_link:
                invite = chat.invite_link

            if not invite:
                print(f"No invite link for {chat.title}")
                continue

            if mode == "request":
                label = f"📩 Request to Join {chat.title}"
            else:
                label = f"🔔 Join {chat.title}"

            buttons.append([InlineKeyboardButton(label, url=invite)])
        except Exception as e:
            print(f"Build button error for {ch.get('id')}: {e}")

    buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="fsub_check")])
    return InlineKeyboardMarkup(buttons)
