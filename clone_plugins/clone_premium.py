# clone_plugins/clone_premium.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import random
import string


@Client.on_message(filters.command("myplan") & filters.private)
async def clone_myplan(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    is_premium = await db.is_premium_user(user_id, bot_username)

    if is_premium:
        text = (
            "💎 **My Premium Status**\n\n"
            "✅ **Status:** Premium (Active)\n"
            "🎁 You have unlimited access.\n\n"
            "• No shortlinks\n"
            "• Unlimited file storage\n"
            "• Priority support"
        )
    else:
        text = (
            "💎 **My Premium Status**\n\n"
            "📌 **Status:** Free\n"
            "🆓 **Limit:** 5 files/day\n\n"
            "Type /plan to see premium plans and upgrade."
        )

    buttons = [[InlineKeyboardButton("💎 View Plans", callback_data="c_plan")],
               [InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
# ==========================================================
# 🔹 /plan COMMAND — Shows the plan text (only when set)
# ==========================================================
@Client.on_message(filters.command("plan") & filters.private)
async def clone_plan_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    plan_text = await db.get_premium_plan_text(bot_username)

    if not plan_text:
        return await message.reply_text(
            "❌ **Plan Not Available**\n\n"
            "ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ʜᴀs ɴᴏᴛ ʙᴇᴇɴ sᴇᴛ ʏᴇᴛ.\n\n"
            "ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ."
        )

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(
        f"💎 **PREMIUM PLAN**\n\n{plan_text}",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
    
@Client.on_message(filters.command("redeem") & filters.private)
async def clone_redeem(client: Client, message: Message):
    if len(message.command) < 2:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await message.reply_text("⚠️ Usage: /redeem [code]", reply_markup=InlineKeyboardMarkup(buttons))

    code = message.command[1].upper()
    record = await db.redeem_premium_code(code, message.from_user.id)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    if not record:
        return await message.reply_text("❌ Invalid or already used code.", reply_markup=InlineKeyboardMarkup(buttons))

    await db.set_user_plan(message.from_user.id, "premium")
    await message.reply_text(
        f"🎉 Redeemed {record['duration_days']} days of Premium!",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_message(filters.command("createcode") & filters.private)
async def clone_createcode(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != message.from_user.id:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await message.reply_text("❌ Owner only command.", reply_markup=InlineKeyboardMarkup(buttons))

    if len(message.command) < 2:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await message.reply_text("⚠️ Usage: /createcode [days]", reply_markup=InlineKeyboardMarkup(buttons))

    try:
        days = int(message.command[1])
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await message.reply_text("❌ Invalid number of days.", reply_markup=InlineKeyboardMarkup(buttons))

    code = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
    await db.create_premium_code(code, days, message.from_user.id)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(
        f"✅ Code created: `{code}` ({days} days)",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
