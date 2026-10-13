# clone_plugins/clone_premium.py
from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
import random
import string


@Client.on_message(filters.command("myplan") & filters.private)
async def clone_myplan(client: Client, message: Message):
    user = await db.get_user(message.from_user.id)
    plan = user.get("plan", "free") if user else "free"
    if plan == "free":
        await message.reply_text(
            "💎 Premium Plan\n\n"
            "📌 Current: Free\n"
            "🆓 Limit: 5 files/day"
        )
    else:
        await message.reply_text(
            "💎 Premium Plan\n\n"
            "📌 Current: Premium\n"
            "✅ Active"
        )


@Client.on_message(filters.command("redeem") & filters.private)
async def clone_redeem(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /redeem [code]")

    code = message.command[1].upper()
    record = await db.redeem_premium_code(code, message.from_user.id)
    if not record:
        return await message.reply_text("❌ Invalid or already used code.")

    await db.set_user_plan(message.from_user.id, "premium")
    await message.reply_text(
        f"🎉 Redeemed {record['duration_days']} days of Premium!"
    )


@Client.on_message(filters.command("createcode") & filters.private)
async def clone_createcode(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != message.from_user.id:
        return await message.reply_text("❌ Owner only command.")

    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /createcode [days]")

    try:
        days = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid number of days.")

    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
    await db.create_premium_code(code, days, message.from_user.id)
    await message.reply_text(f"✅ Code created: `{code}` ({days} days)")
