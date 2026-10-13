# utils/fsub_middleware.py
from database import db
from utils.fsub_helper import check_subscription, build_fsub_keyboard
from config import OWNER_ID


async def check_force_sub(client, message, bot_username):
    """
    Returns True  → user allowed to proceed
    Returns False → force-sub popup already sent
    """
    try:
        user_id = message.from_user.id

        # ==========================================================
        # ✅ CHECK 1: MAIN BOT OWNER → always allowed
        # ==========================================================
        if user_id == OWNER_ID:
            return True

        # ==========================================================
        # ✅ CHECK 2: CLONE OWNER + CLONE ADMINS → allowed
        # ==========================================================
        try:
            clone_data = await db.get_clone_by_username(bot_username)
            if clone_data:
                # Clone owner
                if clone_data.get("user_id") == user_id:
                    return True
                # Clone admins
                if user_id in clone_data.get("admins", []):
                    return True
        except Exception as e:
            print(f"Clone data check error: {type(e).__name__}: {e}")

        # ==========================================================
        # ✅ CHECK 3: Is bot itself admin? (bot owner safety net)
        # ==========================================================
        try:
            bot_owner_data = await db.get_clone_by_username(bot_username)
            if bot_owner_data and bot_owner_data.get("user_id") == user_id:
                return True
        except Exception:
            pass

        # ==========================================================
        # FORCE SUB CHECK — only for regular users
        # ==========================================================
        fsub_status = await db.get_fsub_status(bot_username)
        if not fsub_status:
            return True

        not_joined = await check_subscription(client, user_id, bot_username)
        if not not_joined:
            return True

        # Send popup
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
        print(f"Force sub middleware error: {type(e).__name__}: {e}")
        return True  # On error, allow (don't block users)


async def is_bot_owner(client, user_id, bot_username):
    """
    Check if user is the OWNER of this bot (main or clone).
    Returns True/False.
    """
    try:
        # Main bot owner
        if user_id == OWNER_ID:
            return True

        # Clone bot owner
        clone_data = await db.get_clone_by_username(bot_username)
        if clone_data and clone_data.get("user_id") == user_id:
            return True

        # Clone admin
        if clone_data and user_id in clone_data.get("admins", []):
            return True

    except Exception as e:
        print(f"is_bot_owner error: {type(e).__name__}: {e}")

    return False
