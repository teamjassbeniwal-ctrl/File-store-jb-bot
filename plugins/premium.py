# plugins/premium.py
from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from datetime import datetime, timedelta

# ==========================================================
# 🔹 /myplan COMMAND
# ==========================================================
@Client.on_message(filters.command("myplan") & filters.private)
async def myplan_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if not user:
        return await message.reply_text("❌ Please run /start first.")

    plan = user.get("plan", "free")

    if plan == "free":
        text = (
            "💎 **Premium Plan**\n\n"
            "📌 **Current Plan:** Free\n"
            "🆓 **Usage Limit:** 5 files/day\n\n"
            "✨ **Upgrade to Premium** to unlock:\n"
            "• Unlimited file storage\n"
            "• Custom captions & thumbnails\n"
            "• No shortlink verification\n"
            "• Priority support"
        )
    else:
        text = (
            "💎 **Premium Plan**\n\n"
            "📌 **Current Plan:** Premium\n"
            "✅ **Status:** Active\n"
            "🎁 **Enjoy unlimited access!**"
        )

    await message.reply_text(text)


# ==========================================================
# 🔹 /redeem COMMAND
# ==========================================================
@Client.on_message(filters.command("redeem") & filters.private)
async def redeem_cmd(client: Client, message: Message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ **Usage:** `/redeem <code>`"
        )

    code = message.command[1].upper()
    record = await db.redeem_premium_code(code, user_id)

    if not record:
        return await message.reply_text("❌ Invalid or already used code.")

    await db.set_user_plan(user_id, "premium")

    await message.reply_text(
        f"🎉 **Congratulations!**\n\n"
        f"✅ You have redeemed a `{record['duration_days']}` day Premium plan.\n"
        f"Enjoy your benefits!"
    )
