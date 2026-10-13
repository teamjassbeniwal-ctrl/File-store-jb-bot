# plugins/admin.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from config import OWNER_ID
import asyncio
import random
import string

# ==========================================================
# 🔹 /broadcast COMMAND (Owner Only)
# ==========================================================
@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_cmd(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id != OWNER_ID:
        return await message.reply_text("❌ **Owner only command.**")

    if not message.reply_to_message:
        return await message.reply_text(
            "⚠️ **Reply to a message to broadcast it.**\n\n"
            "Usage: Reply to any message with `/broadcast`"
        )

    users = await db.get_all_users()
    total = len(users)
    success = 0
    failed = 0

    status = await message.reply_text(f"📢 **Broadcasting to {total} users...**")

    for user in users:
        try:
            await message.reply_to_message.copy(user["user_id"])
            success += 1
            await asyncio.sleep(0.05)  # Avoid flood
        except Exception:
            failed += 1

    await status.edit_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"👥 Total: `{total}`\n"
        f"✅ Success: `{success}`\n"
        f"❌ Failed: `{failed}`"
    )


# ==========================================================
# 🔹 /ban COMMAND (Owner Only)
# ==========================================================
@Client.on_message(filters.command("ban") & filters.private)
async def ban_cmd(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id != OWNER_ID:
        return await message.reply_text("❌ **Owner only command.**")

    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ **Usage:** `/ban <user_id>` or reply to a user's message."
        )

    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID.")

    await db.ban_user(target_id)
    await message.reply_text(f"✅ User `{target_id}` has been banned.")


# ==========================================================
# 🔹 /unban COMMAND (Owner Only)
# ==========================================================
@Client.on_message(filters.command("unban") & filters.private)
async def unban_cmd(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id != OWNER_ID:
        return await message.reply_text("❌ **Owner only command.**")

    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** `/unban <user_id>`")

    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID.")

    await db.unban_user(target_id)
    await message.reply_text(f"✅ User `{target_id}` has been unbanned.")


# ==========================================================
# 🔹 /createcode COMMAND (Owner Only - Premium Code Generator)
# ==========================================================
@Client.on_message(filters.command("createcode") & filters.private)
async def createcode_cmd(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id != OWNER_ID:
        return await message.reply_text("❌ **Owner only command.**")

    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ **Usage:** `/createcode <days>`\n"
            "Example: `/createcode 30` creates a 30-day code."
        )

    try:
        days = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid number of days.")

    # Generate a random 12-char code
    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))

    await db.create_premium_code(code, days, user_id)

    await message.reply_text(
        f"✅ **Premium Code Created**\n\n"
        f"🎟️ Code: `{code}`\n"
        f"📅 Duration: `{days} days`\n\n"
        f"Users can redeem it with `/redeem {code}`"
    )
