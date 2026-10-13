# clone_plugins/clone_start.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import asyncio
import os
import psutila
import time

# Temporary edit states
edit_states = {}

# Track bot start time
BOT_START_TIME = time.time()


# ==========================================================
# 🔹 /start
# ==========================================================
@Client.on_message(filters.command("start") & filters.private)
async def clone_start(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    bot_mention = f"@{bot_username}"
    user_mention = message.from_user.mention

    # Deep link handling
    if len(message.command) > 1:
        payload = message.command[1]

        if payload == "customize":
            clone_data = await db.get_clone_by_username(bot_username)
            if clone_data and clone_data["user_id"] == user_id:
                await send_clone_settings(message)
                return
            else:
                await message.reply_text("⚠️ Only the bot owner can customize this bot.")
                return

        stored = await db.get_stored_file(payload)
        if stored:
            if stored["type"] == "single":
                fid = stored["file_id"]
                if fid.startswith("text:"):
                    await message.reply_text(fid.replace("text:", ""))
                else:
                    await message.reply_cached_media(fid, caption="📁 **Here is your file**")
            elif stored["type"] == "batch":
                await message.reply_text(f"📦 Sending {stored['count']} files...")
                for i in range(stored["count"]):
                    try:
                        await client.copy_message(
                            chat_id=message.chat.id,
                            from_chat_id=stored["from_chat_id"],
                            message_id=stored["start_id"] + i
                        )
                    except Exception:
                        pass
            return
        else:
            await message.reply_text("❌ Invalid or expired link.")
            return

    # Custom start text/pic/buttons
    clone_data = await db.get_clone_by_username(bot_username)
    start_text = clone_data.get("start_text") if clone_data else None
    start_pic = clone_data.get("start_pic") if clone_data else None
    start_buttons = clone_data.get("start_buttons", []) if clone_data else []

    if not start_text:
        start_text = (
            "ʜᴇʏ {mention} 👋,\n\n"
            "ᴍʏ ɴᴀᴍᴇ ɪs {bot_mention}\n\n"
            "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴀɴᴅ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss sᴛᴏʀᴇᴅ ᴍᴇssᴀɢᴇs ʙʏ ᴜsɪɴɢ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɢɪᴠᴇɴ ʙʏ ᴍᴇ.\n\n"
            "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
        )

    try:
        formatted_text = start_text.format(mention=user_mention, bot_mention=bot_mention)
    except Exception:
        formatted_text = start_text

    keyboard = []
    for btn in start_buttons:
        keyboard.append([InlineKeyboardButton(btn["text"], url=btn["url"])])

    if not keyboard:
        keyboard = [
            [InlineKeyboardButton("Help", callback_data="c_help"),
             InlineKeyboardButton("About", callback_data="c_about")],
            [InlineKeyboardButton("Settings", callback_data="c_settings")],
            [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
             InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if start_pic:
        await message.reply_photo(photo=start_pic, caption=formatted_text, reply_markup=reply_markup)
    else:
        await message.reply_text(formatted_text, reply_markup=reply_markup)


# ==========================================================
# 🔹 /help
# ==========================================================
@Client.on_message(filters.command("help") & filters.private)
async def clone_help_cmd(client: Client, message: Message):
    await send_clone_help(message)


@Client.on_callback_query(filters.regex("^c_help$"))
async def clone_help_cb(client: Client, callback_query: CallbackQuery):
    await send_clone_help(callback_query.message, edit=True)


async def send_clone_help(message, edit=False):
    text = (
        "🎓 **HELP MENU:**\n\n"
        "🤖 ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ\n"
        "📨 ᴍʏ ɴᴀᴍᴇ ɪꜱ ꜰɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ʙᴜᴛ ɪ ᴄᴀɴ ꜱᴛᴏʀᴇ ᴀɴʏ ᴛʏᴘᴇ ᴏꜰ ᴄᴏɴᴛᴇɴᴛ, ɪɴᴄʟᴜᴅɪɴɢ ᴍᴇꜱꜱᴀɢᴇꜱ, ᴘʜᴏᴛᴏꜱ, ᴠɪᴅᴇᴏꜱ, ᴀɴᴅ ꜰɪʟᴇꜱ.\n"
        "📂 ʏᴏᴜ ᴄᴀɴ ꜱᴛᴏʀᴇ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ʏᴏᴜʀ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴅɪɴɢ ᴍᴇ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ.\n"
        "🔐 ɪꜰ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴏʀ ɢʀᴏᴜᴘ ɪꜱ ᴘʀɪᴠᴀᴛᴇ, ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ꜰɪʀꜱᴛ.\n"
        "🔗 ᴀꜰᴛᴇʀ ꜱᴛᴏʀɪɴɢ, ɪ ᴡɪʟʟ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ꜰᴏʀ ɪɴꜱᴛᴀɴᴛ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ʏᴏᴜʀ ꜰɪʟᴇꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "📚 **BASIC COMMANDS**\n\n"
        "➤ /start - ᴄʜᴇᴄᴋ ɪꜰ ɪ'ᴍ ᴀʟɪᴠᴇ.\n"
        "➤ /id - ɢᴇᴛ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "📦 **FILE STORAGE COMMANDS**\n\n"
        "➤ /link - ꜱᴛᴏʀᴇ ᴀ ꜱɪɴɢʟᴇ ꜰɪʟᴇ ᴏʀ ᴍᴇꜱꜱᴀɢᴇ.\n"
        "➤ /batch - ꜱᴛᴏʀᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴄᴏɴꜱᴇᴄᴜᴛɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ꜰʀᴏᴍ ᴀ ᴄʜᴀɴɴᴇʟ.\n"
        "➤ /custom_batch - ꜱᴛᴏʀᴇ ᴍᴜʟᴛɪᴘʟᴇ ʀᴀɴᴅᴏᴍ ᴍᴇꜱꜱᴀɢᴇꜱ.\n"
        "➤ /multiple_batch - ᴄʀᴇᴀᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ʙᴀᴛᴄʜ ʟɪɴᴋꜱ ᴀᴛ ᴏɴᴄᴇ.\n"
        "➤ /special_link - ᴄʀᴇᴀᴛᴇ ꜱᴘᴇᴄɪᴀʟ ʟɪɴᴋꜱ ᴡɪᴛʜ ᴄᴜꜱᴛᴏᴍ ꜱᴇᴛᴛɪɴɢꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "💎 **PREMIUM COMMANDS**\n\n"
        "➤ /createcode - ᴄʀᴇᴀᴛᴇ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇꜱ.\n"
        "➤ /redeem - ʀᴇᴅᴇᴇᴍ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ.\n"
        "➤ /myplan - ᴠɪᴇᴡ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴅᴇᴛᴀɪʟꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "⚙️ **USER SETTINGS**\n\n"
        "➤ /settings - ᴄᴜꜱᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ꜱᴇᴛᴛɪɴɢꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "👑 **ADMIN COMMANDS**\n\n"
        "➤ /customize - ᴄᴜꜱᴛᴏᴍɪᴢᴇ ᴄʟᴏɴᴇ ʙᴏᴛ ꜱᴇᴛᴛɪɴɢꜱ.\n"
        "➤ /broadcast - ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ.\n"
        "➤ /ban - ʙᴀɴ ᴀ ᴜꜱᴇʀ ꜰʀᴏᴍ ᴛʜᴇ ʙᴏᴛ.\n"
        "➤ /unban - ᴜɴʙᴀɴ ᴀ ᴘʀᴇᴠɪᴏᴜꜱʟʏ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀ."
    )
    buttons = [
        [InlineKeyboardButton("Settings", callback_data="c_settings"),
         InlineKeyboardButton("About", callback_data="c_about")],
        [InlineKeyboardButton("Back", callback_data="c_back")]
    ]
    if edit:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 /about
# ==========================================================
@Client.on_callback_query(filters.regex("^c_about$"))
async def clone_about_cb(client: Client, callback_query: CallbackQuery):
    text = (
        "○ **Creator** : King VJ\n"
        "○ **Language** : Python3\n"
        "○ **Library** : Pyrogram 2.0.106\n"
        "○ **Channel** : @teamjb1\n"
        "○ **Support Group** : @jbsupportgroup"
    )
    buttons = [
        [InlineKeyboardButton("Settings", callback_data="c_settings"),
         InlineKeyboardButton("Help", callback_data="c_help")],
        [InlineKeyboardButton("Back", callback_data="c_back")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 /id
# ==========================================================
@Client.on_message(filters.command("id") & filters.private)
async def clone_id_cmd(client: Client, message: Message):
    user = message.from_user
    text = (
        "User Details :\n\n\n"
        f"🦚 **First Name** : {user.first_name}\n\n"
        f"🐧 **Last Name** : {user.last_name or 'None'}\n\n"
        f"👤 **User Id** : `{user.id}`\n\n"
        f"👦 **Username** : @{user.username or 'None'}\n\n"
        f"🔗 **User Link** : {user.mention}\n\n"
        f"🌟 **Telegram Premium** : {'True' if user.is_premium else 'False'}\n\n"
        f"📃 **Language Code** : {user.language_code}\n\n"
        "💫 **Status** : Recently"
    )
    await message.reply_text(text)


# ==========================================================
# 🔹 /settings
# ==========================================================
@Client.on_message(filters.command("settings") & filters.private)
async def clone_settings_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != message.from_user.id:
        return await message.reply_text("⚠️ Only the bot owner can use this command.")

    await send_clone_settings(message)


@Client.on_callback_query(filters.regex("^c_settings$"))
async def clone_settings_cb(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if not clone_data or clone_data["user_id"] != callback_query.from_user.id:
        return await callback_query.answer("Owner only!", show_alert=True)
    await send_clone_settings(callback_query.message, edit=True)


async def send_clone_settings(message, edit=False):
    text = (
        "🛠️ **CLONE MENU**\n\n"
        "WELCOME TO YOUR CLONE BOT MANAGEMENT HUB!\n"
        "Customize your bot settings or manage its status using the options below.\n\n"
        "⚙️ **QUICK COMMANDS**\n"
        "🚀 /activate — Activate your clone bot\n"
        "🗑️ /delete — Permanently delete your clone bot\n\n"
        "🎨 **BOT CUSTOMIZATION**\n"
        "✨ Click a button below to modify settings, welcome message, and features."
    )
    buttons = [
        [InlineKeyboardButton("💰 MONETIZATION", callback_data="c_monetization"),
         InlineKeyboardButton("📝 START MESSAGE", callback_data="c_start_msg")],
        [InlineKeyboardButton("📢 LOG CHANNEL", callback_data="c_log_channel"),
         InlineKeyboardButton("☁️ DATABASE CHANNEL", callback_data="c_db_channel")],
        [InlineKeyboardButton("👥 ADMINS", callback_data="c_admins"),
         InlineKeyboardButton("📊 BOT STATUS", callback_data="c_status")],
        [InlineKeyboardButton("🛍️ BOT MODE", callback_data="c_bot_mode"),
         InlineKeyboardButton("⏱️ RESTART BOT", callback_data="c_restart")],
        [InlineKeyboardButton("🚫 DELETE BOT", callback_data="c_delete_bot"),
         InlineKeyboardButton("🔍 MORE FEATURES", callback_data="c_more_features")],
        [InlineKeyboardButton("🔙 BACK", callback_data="c_back")]
    ]
    if edit:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 LOG CHANNEL
# ==========================================================
@Client.on_callback_query(filters.regex("^c_log_channel$"))
async def log_channel_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    log_channel = clone_data.get("log_channel") if clone_data else None

    if log_channel:
        text = (
            "📢 **LOG CHANNEL:**\n\n"
            "ᴡʜᴀᴛ ɪs ʟᴏɢ ᴄʜᴀɴɴᴇʟ ??\n\n"
            "ɪꜰ ɴᴇᴡ ᴜsᴇʀs sᴛᴀʀᴛ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ ᴛʜᴇɴ ʙᴏᴛ ɴᴏᴛɪꜰɪᴇs ʏᴏᴜ.\n\n"
            f"✅ **Current Log Channel:** `{log_channel}`"
        )
    else:
        text = (
            "📢 **LOG CHANNEL:**\n\n"
            "ᴡʜᴀᴛ ɪs ʟᴏɢ ᴄʜᴀɴɴᴇʟ ??\n\n"
            "ɪꜰ ɴᴇᴡ ᴜsᴇʀs sᴛᴀʀᴛ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ ᴛʜᴇɴ ʙᴏᴛ ɴᴏᴛɪꜰɪᴇs ʏᴏᴜ.\n\n"
            "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ❗️"
        )

    buttons = [
        [InlineKeyboardButton("Set Log Channel", callback_data="c_set_log")],
        [InlineKeyboardButton("Delete Channel", callback_data="c_delete_log")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_set_log$"))
async def set_log_channel(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    edit_states[user_id] = "waiting_for_log_channel"
    bot_username = (await client.get_me()).username

    text = (
        "ꜰᴏʀᴡᴀʀᴅ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ,\n"
        f"ᴀɴᴅ ᴍᴀᴋᴇ sᴜʀᴇ @{bot_username} ɪs ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ.\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private, group=21)
async def receive_log_channel(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_log_channel":
        return

    if not message.forward_from_chat:
        return await message.reply_text("⚠️ Please forward a message from your log channel.")

    chat = message.forward_from_chat
    if chat.type not in ("channel", "supergroup"):
        return await message.reply_text("⚠️ Only channels/supergroups are allowed.")

    edit_states.pop(user_id, None)

    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "log_channel", chat.id)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
    await message.reply_text(
        f"✅ **Log Channel Set:** {chat.title}\n\n"
        "All future user events will be logged here.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^c_delete_log$"))
async def delete_log_channel(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "log_channel", None)

    await callback_query.answer("✅ Log channel deleted.", show_alert=True)
    await log_channel_menu(client, callback_query)


# ==========================================================
# 🔹 DATABASE CHANNEL
# ==========================================================
@Client.on_callback_query(filters.regex("^c_db_channel$"))
async def db_channel_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    db_channel = clone_data.get("db_channel") if clone_data else None

    if db_channel:
        text = (
            "☁️ **DATABASE CHANNEL:**\n\n"
            "ᴛʜɪs ᴄʜᴀɴɴᴇʟ sᴛᴏʀᴇs ᴀʟʟ ʏᴏᴜʀ ꜰɪʟᴇs.\n\n"
            f"✅ **Current DB Channel:** `{db_channel}`"
        )
    else:
        text = (
            "☁️ **DATABASE CHANNEL:**\n\n"
            "ᴛʜɪs ᴄʜᴀɴɴᴇʟ sᴛᴏʀᴇs ᴀʟʟ ʏᴏᴜʀ ꜰɪʟᴇs.\n\n"
            "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ❗️"
        )

    buttons = [
        [InlineKeyboardButton("Set Database Channel", callback_data="c_set_db")],
        [InlineKeyboardButton("Delete Channel", callback_data="c_delete_db")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_set_db$"))
async def set_db_channel(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    edit_states[user_id] = "waiting_for_db_channel"
    bot_username = (await client.get_me()).username

    text = (
        "ꜰᴏʀᴡᴀʀᴅ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ,\n"
        f"ᴀɴᴅ ᴍᴀᴋᴇ sᴜʀᴇ @{bot_username} ɪs ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ.\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private, group=22)
async def receive_db_channel(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_db_channel":
        return

    if not message.forward_from_chat:
        return await message.reply_text("⚠️ Please forward a message from your DB channel.")

    chat = message.forward_from_chat
    if chat.type not in ("channel", "supergroup"):
        return await message.reply_text("⚠️ Only channels/supergroups are allowed.")

    edit_states.pop(user_id, None)

    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "db_channel", chat.id)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
    await message.reply_text(
        f"✅ **Database Channel Set:** {chat.title}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^c_delete_db$"))
async def delete_db_channel(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "db_channel", None)

    await callback_query.answer("✅ Database channel deleted.", show_alert=True)
    await db_channel_menu(client, callback_query)


# ==========================================================
# 🔹 ADMINS
# ==========================================================
@Client.on_callback_query(filters.regex("^c_admins$"))
async def admins_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    admins = clone_data.get("admins", []) if clone_data else []

    text = (
        "👥 **ADMINS:**\n\n"
        "ᴀᴅᴍɪɴs ᴄᴀɴ sᴛᴏʀᴇ ꜰɪʟᴇs ᴀɴᴅ ɢᴇɴᴇʀᴀᴛᴇ ʟɪɴᴋs ᴡɪᴛʜᴏᴜᴛ ʟɪᴍɪᴛs.\n\n"
        f"👤 **Total Admins:** {len(admins)}"
    )

    buttons = [
        [InlineKeyboardButton("Add Admin", callback_data="c_add_admin"),
         InlineKeyboardButton("Remove Admin", callback_data="c_remove_admin")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_add_admin$"))
async def add_admin_prompt(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    edit_states[user_id] = "waiting_for_add_admin"

    text = (
        "👥 **ADD ADMIN**\n\n"
        "ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴜsᴇʀ ᴏʀ sᴇɴᴅ ᴛʜᴇɪʀ ᴜsᴇʀ ɪᴅ.\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=23)
async def receive_add_admin(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_add_admin":
        return

    try:
        new_admin = int(message.text.strip())
    except ValueError:
        return await message.reply_text("❌ Invalid user ID.")

    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if clone_data:
        admins = clone_data.get("admins", [])
        if new_admin not in admins:
            admins.append(new_admin)
            await db.update_clone_setting(clone_data["user_id"], "admins", admins)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await message.reply_text(f"✅ Admin {new_admin} added.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_remove_admin$"))
async def remove_admin_prompt(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    edit_states[user_id] = "waiting_for_remove_admin"

    text = (
        "👥 **REMOVE ADMIN**\n\n"
        "ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴛʜᴇ ᴜsᴇʀ ᴏʀ sᴇɴᴅ ᴛʜᴇɪʀ ᴜsᴇʀ ɪᴅ.\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=24)
async def receive_remove_admin(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_remove_admin":
        return

    try:
        rem_admin = int(message.text.strip())
    except ValueError:
        return await message.reply_text("❌ Invalid user ID.")

    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if clone_data:
        admins = clone_data.get("admins", [])
        if rem_admin in admins:
            admins.remove(rem_admin)
            await db.update_clone_setting(clone_data["user_id"], "admins", admins)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await message.reply_text(f"✅ Admin {rem_admin} removed.", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 BOT STATUS
# ==========================================================
@Client.on_callback_query(filters.regex("^c_status$"))
async def bot_status(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    total_users = await db.users.count_documents({})
    banned_users = await db.banned_users.count_documents({})

    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent

    uptime_seconds = int(time.time() - BOT_START_TIME)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    text = (
        f"**{bot_username.upper()}**\n\n"
        f"**USERS** - {total_users}\n\n"
        f"**BAN USERS** - {banned_users}\n\n"
        f"**CPU** - {cpu}%\n\n"
        f"**RAM** - {ram}%\n\n"
        f"**UPTIME** - {hours} Hours {minutes} Minutes {seconds} Seconds"
    )

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_settings")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 BOT MODE
# ==========================================================
@Client.on_callback_query(filters.regex("^c_bot_mode$"))
async def bot_mode_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    current_mode = clone_data.get("bot_mode", "public") if clone_data else "public"
    mode_icon = "🌐" if current_mode == "public" else "🔒"

    text = (
        "🛍️ **BOT MODE:**\n\n"
        f"{mode_icon} **Current Mode:** {current_mode.title()}\n\n"
        "• **Public** - Anyone can use the bot\n"
        "• **Private** - Only admins can use the bot"
    )

    buttons = [
        [InlineKeyboardButton("🌐 Public", callback_data="c_mode_public"),
         InlineKeyboardButton("🔒 Private", callback_data="c_mode_private")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_mode_(public|private)$"))
async def set_bot_mode(client: Client, callback_query: CallbackQuery):
    mode = callback_query.data.split("_")[-1]
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "bot_mode", mode)

    await callback_query.answer(f"Mode set to {mode.title()} ✅", show_alert=True)
    await bot_mode_menu(client, callback_query)


# ==========================================================
# 🔹 RESTART BOT
# ==========================================================
@Client.on_callback_query(filters.regex("^c_restart$"))
async def restart_bot(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("⏱️ Restarting clone bot...", show_alert=True)
    await asyncio.sleep(2)
    # Gracefully restart the clone bot's client
    await client.restart()
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_settings")]]
    await callback_query.message.edit_text("✅ Bot restarted successfully!", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 DELETE BOT
# ==========================================================
@Client.on_callback_query(filters.regex("^c_delete_bot$"))
async def delete_bot_prompt(client: Client, callback_query: CallbackQuery):
    text = (
        "🚫 **DELETE BOT**\n\n"
        "Are you sure? This will permanently delete your clone bot and all its data.\n\n"
        "This action cannot be undone."
    )
    buttons = [
        [InlineKeyboardButton("❌ Cancel", callback_data="c_settings"),
         InlineKeyboardButton("🚫 Delete", callback_data="c_confirm_delete_bot")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_confirm_delete_bot$"))
async def confirm_delete_bot(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if clone_data:
        await db.delete_clone(clone_data["user_id"])

    await callback_query.message.edit_text(
        "✅ **Bot deleted.**\n\n"
        "You can now create a new clone from the main bot with /clone."
    )


# ==========================================================
# 🔹 MORE FEATURES
# ==========================================================
@Client.on_callback_query(filters.regex("^c_more_features$"))
async def more_features(client: Client, callback_query: CallbackQuery):
    text = (
        "🔍 **MORE FEATURES**\n\n"
        "Here are the settings command features:\n\n"
        "• `/settings` - Open this menu\n"
        "• `/broadcast` - Send a message to all users\n"
        "• `/ban [user_id]` - Ban a user\n"
        "• `/unban [user_id]` - Unban a user\n"
        "• `/createcode [days]` - Generate premium codes\n"
        "• `/myplan` - View your premium plan\n"
        "• `/link` - Store a file\n"
        "• `/batch` - Store multiple files"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_settings")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 BACK
# ==========================================================
@Client.on_callback_query(filters.regex("^c_back$"))
async def clone_back_cb(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    bot_mention = f"@{bot_username}"
    user_mention = callback_query.from_user.mention

    clone_data = await db.get_clone_by_username(bot_username)
    start_text = clone_data.get("start_text") if clone_data else None
    start_buttons = clone_data.get("start_buttons", []) if clone_data else []

    if not start_text:
        start_text = (
            "ʜᴇʏ {mention} 👋,\n\n"
            "ᴍʏ ɴᴀᴍᴇ ɪs {bot_mention}\n\n"
            "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴀɴᴅ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss sᴛᴏʀᴇᴅ ᴍᴇssᴀɢᴇs ʙʏ ᴜsɪɴɢ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɢɪᴠᴇɴ ʙʏ ᴍᴇ.\n\n"
            "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
        )

    try:
        formatted = start_text.format(mention=user_mention, bot_mention=bot_mention)
    except Exception:
        formatted = start_text

    keyboard = []
    for btn in start_buttons:
        keyboard.append([InlineKeyboardButton(btn["text"], url=btn["url"])])

    if not keyboard:
        keyboard = [
            [InlineKeyboardButton("Help", callback_data="c_help"),
             InlineKeyboardButton("About", callback_data="c_about")],
            [InlineKeyboardButton("Settings", callback_data="c_settings")],
            [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
             InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
        ]

    await callback_query.message.edit_text(formatted, reply_markup=InlineKeyboardMarkup(keyboard))


# ==========================================================
# 🔹 CANCEL
# ==========================================================
@Client.on_message(filters.command("cancel") & filters.private, group=25)
async def cancel_clone_edit(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in edit_states:
        edit_states.pop(user_id, None)
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_settings")]]
        await message.reply_text("✅ Cancelled.", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 /broadcast
# ==========================================================
@Client.on_message(filters.command("broadcast") & filters.private)
async def clone_broadcast(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != user_id:
        return await message.reply_text("❌ Owner only command.")

    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a message to broadcast.")

    users = await db.get_all_users()
    status = await message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    success = 0
    for user in users:
        try:
            await message.reply_to_message.copy(user["user_id"])
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await status.edit_text(f"✅ Done! Sent to {success}/{len(users)} users.")


# ==========================================================
# 🔹 /ban and /unban
# ==========================================================
@Client.on_message(filters.command("ban") & filters.private)
async def clone_ban(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != user_id:
        return await message.reply_text("❌ Owner only command.")

    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /ban [user_id]")

    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID.")

    await db.ban_user(target_id)
    await message.reply_text(f"✅ User {target_id} banned.")


@Client.on_message(filters.command("unban") & filters.private)
async def clone_unban(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != user_id:
        return await message.reply_text("❌ Owner only command.")

    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /unban [user_id]")

    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid user ID.")

    await db.unban_user(target_id)
    await message.reply_text(f"✅ User {target_id} unbanned.")
