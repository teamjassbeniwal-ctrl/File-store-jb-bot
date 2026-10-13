# utils/fsub_middleware.py
from database import db
from utils.fsub_helper import check_subscription, build_fsub_keyboard


async def check_force_sub(client, message, bot_username):
    """
    Check if user has joined all force-sub channels.
    Returns True if user is verified (or force sub is off).
    Returns False if user needs to join (popup already sent).
    """
    try:
        fsub_status = await db.get_fsub_status(bot_username)
        if not fsub_status:
            return True  # Force sub off — allow

        user_id = message.from_user.id
        not_joined = await check_subscription(client, user_id, bot_username)

        if not not_joined:
            return True  # User joined all — allow

        # User needs to join — send popup
        fsub_text = await db.get_fsub_text(bot_username)
        fsub_img = await db.get_fsub_image(bot_username)
        keyboard = await build_fsub_keyboard(client, bot_username, not_joined)

        default_text = (
            "📢 **Please Join Our Channels**\n\n"
            "To use this bot, you must join the channels below.\n"
            "After joining, click **✅ I Joined**."
        )
        msg_text = fsub_text or default_text

        if fsub_img:
            await message.reply_photo(
                photo=fsub_img,
                caption=msg_text,
                reply_markup=keyboard
            )
        else:
            await message.reply_text(
                msg_text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        return False

    except Exception as e:
        print(f"Force sub middleware error: {e}")
        return True  # On error, allow (so bot doesn't get stuck)
