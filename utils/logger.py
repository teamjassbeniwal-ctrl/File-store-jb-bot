# utils/logger.py
"""
Centralized Master Logging System
Sends authorized media logs from Main Bot and all Clone Bots to the Master Log Channel.
"""
from datetime import datetime
from database import db
from config import MASTER_LOG_CHANNEL, MASTER_LOG_ENABLED


def _fmt_time():
    """Format current time."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")


def _detect_media(message):
    """
    Detect media type, file name, and size from a Pyrogram message.
    Returns (media_type, file_name, file_size).
    """
    media_type = "unknown"
    file_name = "N/A"
    file_size = "N/A"

    try:
        if message.document:
            media_type = "Document"
            file_name = message.document.file_name or "document"
            file_size = f"{round(message.document.file_size / 1024 / 1024, 2)} MB"
        elif message.video:
            media_type = "Video"
            file_name = message.video.file_name or "video"
            file_size = f"{round(message.video.file_size / 1024 / 1024, 2)} MB"
        elif message.photo:
            media_type = "Photo"
            file_name = "photo.jpg"
            file_size = "N/A"
        elif message.audio:
            media_type = "Audio"
            file_name = message.audio.file_name or "audio"
            file_size = f"{round(message.audio.file_size / 1024 / 1024, 2)} MB"
        elif message.voice:
            media_type = "Voice"
            file_name = "voice.ogg"
            file_size = f"{round(message.voice.file_size / 1024 / 1024, 2)} MB"
        elif message.video_note:
            media_type = "Video Note"
            file_name = "video_note"
        elif message.animation:
            media_type = "Animation"
            file_name = message.animation.file_name or "animation"
        elif message.text:
            media_type = "Text"
            file_name = f"Text: {message.text[:50]}"
    except Exception:
        pass

    return media_type, file_name, file_size


async def send_master_log(
    client,
    event_type: str,
    user_id: int = None,
    username: str = None,
    bot_username: str = None,
    clone_owner_id: int = None,
    message=None,
    extra: str = None,
    forward_media: bool = False
):
    """
    Send a centralized log to the Master Log Channel.

    event_type: "media_upload", "media_delivery", "clone_created", "error", "info"
    forward_media: If True and message has media, forward media with caption.
    """
    if not MASTER_LOG_ENABLED or not MASTER_LOG_CHANNEL:
        return

    try:
        # Detect media info
        media_type = "N/A"
        file_name = "N/A"
        file_size = "N/A"
        if message:
            media_type, file_name, file_size = _detect_media(message)

        # Build log text
        lines = [f"🔔 **CENTRAL LOG — {event_type.upper()}**\n"]
        lines.append(f"🕐 **Time:** `{_fmt_time()}`")

        if bot_username:
            lines.append(f"🤖 **Bot:** @{bot_username}")
        if clone_owner_id:
            lines.append(f"👑 **Clone Owner ID:** `{clone_owner_id}`")
        if user_id:
            lines.append(f"👤 **User ID:** `{user_id}`")
        if username:
            lines.append(f"📛 **Username:** @{username}")

        if media_type != "N/A":
            lines.append(f"📁 **Type:** {media_type}")
            lines.append(f"📄 **File:** `{file_name}`")
            lines.append(f"📦 **Size:** {file_size}")

        if extra:
            lines.append(f"\n📝 {extra}")

        text = "\n".join(lines)

        # Try to forward media with caption
        if forward_media and message and (message.document or message.video or
                                          message.photo or message.audio or
                                          message.voice or message.animation):
            try:
                await message.copy(MASTER_LOG_CHANNEL, caption=text)
                return True
            except Exception as e:
                print(f"[MASTER LOG] Media forward failed: {e}")
                # Fallback to text-only
                pass

        # Send text-only log
        await client.send_message(
            MASTER_LOG_CHANNEL,
            text,
            disable_web_page_preview=True
        )
        return True

    except Exception as e:
        print(f"[MASTER LOG] Failed to send log: {type(e).__name__}: {e}")
        return False


async def log_media_event(
    client,
    event_type: str,
    message,
    bot_username: str,
    user_id: int,
    username: str,
    clone_owner_id: int = None,
    extra: str = None
):
    """
    Convenience wrapper for media events.
    Sends to master log AND clone owner's log channel (if configured).
    """
    # 1. Master Log (always)
    await send_master_log(
        client=client,
        event_type=event_type,
        user_id=user_id,
        username=username,
        bot_username=bot_username,
        clone_owner_id=clone_owner_id,
        message=message,
        extra=extra,
        forward_media=True
    )

    # 2. Clone Owner Log (if configured)
    if bot_username:
        try:
            clone_data = await db.get_clone_by_username(bot_username)
            owner_log = clone_data.get("log_channel") if clone_data else None

            if owner_log and owner_log != MASTER_LOG_CHANNEL:
                # Build owner-specific text
                media_type, file_name, file_size = _detect_media(message)
                owner_text = (
                    f"📥 **{event_type.replace('_', ' ').title()}**\n\n"
                    f"👤 **User:** `{user_id}`\n"
                    f"📛 **Username:** @{username or 'None'}\n\n"
                    f"📁 **Type:** {media_type}\n"
                    f"📄 **File:** `{file_name}`\n"
                    f"📦 **Size:** {file_size}"
                )
                if extra:
                    owner_text += f"\n\n📝 {extra}"

                try:
                    await message.copy(owner_log, caption=owner_text)
                except Exception:
                    await client.send_message(owner_log, owner_text, disable_web_page_preview=True)
        except Exception as e:
            print(f"[OWNER LOG] Failed: {type(e).__name__}: {e}")


async def log_clone_created(
    client,
    owner_id: int,
    clone_username: str,
    owner_username: str = None
):
    """Log a clone bot creation event."""
    await send_master_log(
        client=client,
        event_type="clone_created",
        user_id=owner_id,
        username=owner_username,
        bot_username=clone_username,
        clone_owner_id=owner_id,
        extra=f"New clone bot created: @{clone_username}"
    )


async def log_error(
    client,
    bot_username: str,
    error_message: str,
    user_id: int = None
):
    """Log an error event."""
    await send_master_log(
        client=client,
        event_type="error",
        user_id=user_id,
        bot_username=bot_username,
        extra=f"⚠️ {error_message}"
    )
