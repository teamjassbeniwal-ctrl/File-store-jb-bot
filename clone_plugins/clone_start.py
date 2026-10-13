# clone_plugins/clone_start.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import asyncio
import psutil
import time

edit_states = {}
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

    # Log new user
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data and clone_data.get("log_channel"):
        try:
            await client.send_message(
                clone_data["log_channel"],
                f"🆕 **New User Started**\n\n"
                f"👤 {message.from_user.first_name}\n"
                f"🆔 `{user_id}`\n"
                f"📛 @{message.from_user.username or 'None'}"
            )
        except Exception as e:
            print(f"Log channel error: {e}")

    # Deep link
    if len(message.command) > 1:
        payload = message.command[1]

        if payload == "customize":
            if clone_data and clone_data["user_id"] == user_id:
                await send_clone_settings(message)
                return
            else:
                return await message.reply_text("⚠️ Only the bot owner can customize this bot.")

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
            return await message.reply_text("❌ Invalid or expired link.")

    # Custom start message
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
            [InlineKeyboardButton("💎 My Plan", callback_data="c_myplan"),
             InlineKeyboardButton("📖 Plans", callback_data="c_plan")],
            [InlineKeyboardButton("Help", callback_data="c_help"),
             InlineKeyboardButton("About", callback_data="c_about")],
            [InlineKeyboardButton("Settings", callback_data="c_settings"),
             InlineKeyboardButton("Customize", url=f"https://t.me/{bot_username}?start=customize")],
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
        "📨 ᴍʏ ɴᴀᴍᴇ ɪꜱ ꜰɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ʙᴜᴛ ɪ ᴄᴀɴ ꜱᴛᴏʀᴇ ᴀɴʏ ᴛʏᴘᴇ ᴏꜰ ᴄᴏɴᴛᴇɴᴛ.\n"
        "📂 ʏᴏᴜ ᴄᴀɴ ꜱᴛᴏʀᴇ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ʏᴏᴜʀ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟ.\n"
        "🔐 ɪꜰ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ɪꜱ ᴘʀɪᴠᴀᴛᴇ, ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ.\n"
        "🔗 ᴀꜰᴛᴇʀ ꜱᴛᴏʀɪɴɢ, ɪ ᴡɪʟʟ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "📚 **BASIC COMMANDS**\n\n"
        "➤ /start - ᴄʜᴇᴄᴋ ɪꜰ ɪ'ᴍ ᴀʟɪᴠᴇ.\n"
        "➤ /id - ɢᴇᴛ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "📦 **FILE STORAGE COMMANDS**\n\n"
        "➤ /link - ꜱᴛᴏʀᴇ ᴀ ꜱɪɴɢʟᴇ ꜰɪʟᴇ.\n"
        "➤ /batch - ꜱᴛᴏʀᴇ ᴍᴜʟᴛɪᴘʟᴇ ꜰɪʟᴇꜱ.\n"
        "➤ /custom_batch - ꜱᴛᴏʀᴇ ʀᴀɴᴅᴏᴍ ꜰɪʟᴇꜱ.\n"
        "➤ /multiple_batch - ᴄʀᴇᴀᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ʙᴀᴛᴄʜ ʟɪɴᴋꜱ.\n"
        "➤ /special_link - ᴄᴜꜱᴛᴏᴍ ʟɪɴᴋꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "💎 **PREMIUM COMMANDS**\n\n"
        "➤ /myplan - ᴠɪᴇᴡ ʏᴏᴜʀ ᴘʟᴀɴ.\n"
        "➤ /redeem - ʀᴇᴅᴇᴇᴍ ᴀ ᴄᴏᴅᴇ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "⚙️ **USER SETTINGS**\n\n"
        "➤ /settings - ᴄᴜꜱᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ ꜱᴇᴛᴛɪɴɢꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "👑 **ADMIN COMMANDS**\n\n"
        "➤ /customize - ᴄᴜꜱᴛᴏᴍɪᴢᴇ ᴄʟᴏɴᴇ ʙᴏᴛ.\n"
        "➤ /broadcast - ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴛᴏ ᴜꜱᴇʀꜱ.\n"
        "➤ /ban [id] - ʙᴀɴ ᴀ ᴜꜱᴇʀ.\n"
        "➤ /unban [id] - ᴜɴʙᴀɴ ᴀ ᴜꜱᴇʀ."
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
# 🔹 /settings — USER SETTINGS MENU
# ==========================================================
@Client.on_message(filters.command("settings") & filters.private)
async def user_settings_cmd(client: Client, message: Message):
    await send_user_settings(message)


@Client.on_callback_query(filters.regex("^c_settings$"))
async def user_settings_cb(client: Client, callback_query: CallbackQuery):
    await send_user_settings(callback_query.message, edit=True)


async def send_user_settings(message, edit=False):
    text = (
        "⚙️ **SETTINGS:**\n\n"
        "ᴄᴜsᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴀs ᴘᴇʀ ʏᴏᴜʀ ɴᴇᴇᴅ.\n\n"
        "ɴᴏᴛᴇ: ᴛʜᴇ sᴇᴛᴛɪɴɢs ʙᴇʟᴏᴡ ᴡɪʟʟ ᴏɴʟʏ ᴡᴏʀᴋ ғᴏʀ ʟɪɴᴋs ᴄʀᴇᴀᴛᴇᴅ ʙʏ ᴛʜɪs ᴛᴇʟᴇɢʀᴀᴍ ᴀᴄᴄᴏᴜɴᴛ. ᴛʜᴇʏ ᴡɪʟʟ ɴᴏᴛ ᴀғғᴇᴄᴛ ʟɪɴᴋs ᴄʀᴇᴀᴛᴇᴅ ʙʏ ᴏᴛʜᴇʀ ᴀᴄᴄᴏᴜɴᴛs."
    )
    buttons = [
        [InlineKeyboardButton("💎 PREMIUM PLAN", callback_data="premium")],
        [InlineKeyboardButton("🆓 FREE USAGE LIMIT", callback_data="u_free_limit")],
        [InlineKeyboardButton("🌍 REFER AND EARN", callback_data="u_refer")],
        [InlineKeyboardButton("🔗 LINK SHORTNER", callback_data="u_shortner")],
        [InlineKeyboardButton("⏰ TOKEN VERIFICATION", callback_data="u_token_verify")],
        [InlineKeyboardButton("📢 FORCE SUBSCRIBE", callback_data="u_force_sub")],
        [InlineKeyboardButton("🍿 CAPTION", callback_data="u_caption"),
         InlineKeyboardButton("🖼️ THUMBNAIL", callback_data="u_thumbnail")],
        [InlineKeyboardButton("⚪ BUTTON", callback_data="u_button"),
         InlineKeyboardButton("♻️ AUTO DELETE", callback_data="u_auto_delete")],
        [InlineKeyboardButton("♾️ PERMANENT LINK", callback_data="u_permanent_link")],
        [InlineKeyboardButton("🔒 PROTECT CONTENT", callback_data="u_protect_content")],
        [InlineKeyboardButton("🔙 BACK", callback_data="c_back")]
    ]
    if edit:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 /customize — CLONE OWNER MENU
# ==========================================================
@Client.on_message(filters.command("customize") & filters.private)
async def customize_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != message.from_user.id:
        return await message.reply_text("⚠️ Only the bot owner can use this command.")

    await send_clone_settings(message)


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
         InlineKeyboardButton("💎 PREMIUM PLAN", callback_data="premium")],
        [InlineKeyboardButton("📝 START MESSAGE", callback_data="c_start_msg"),
         InlineKeyboardButton("📢 LOG CHANNEL", callback_data="c_log_channel")],
        [InlineKeyboardButton("☁️ DATABASE CHANNEL", callback_data="c_db_channel"),
         InlineKeyboardButton("👥 ADMINS", callback_data="c_admins")],
        [InlineKeyboardButton("📊 BOT STATUS", callback_data="c_status"),
         InlineKeyboardButton("🛍️ BOT MODE", callback_data="c_bot_mode")],
        [InlineKeyboardButton("⏱️ RESTART BOT", callback_data="c_restart"),
         InlineKeyboardButton("🚫 DELETE BOT", callback_data="c_delete_bot")],
        [InlineKeyboardButton("🔍 MORE FEATURES", callback_data="c_more_features")],
        [InlineKeyboardButton("🔙 BACK", callback_data="c_back")]
    ]
    if edit:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# ==========================================================
# 🔹 USER SETTINGS CALLBACK HANDLER
# ==========================================================
@Client.on_callback_query(filters.regex("^u_(free_limit|refer|shortner|token_verify|force_sub|caption|thumbnail|button|auto_delete|permanent_link|protect_content)$"))
async def user_setting_handler(client: Client, callback_query: CallbackQuery):
    key = callback_query.data.replace("u_", "")
    messages = {
        "free_limit": "🆓 Free usage: 5 files per day.",
        "refer": "🌍 Refer & Earn: Coming soon!",
        "shortner": "🔗 Shortlink: Configure shortlink API.",
        "token_verify": "⏰ Token Verification: Toggle on/off.",
        "force_sub": "📢 Force Subscribe: Require channel join.",
        "caption": "🍿 Caption: Send caption text.",
        "thumbnail": "🖼️ Thumbnail: Send a photo.",
        "button": "⚪ Button: Configure custom buttons.",
        "auto_delete": "♻️ Auto Delete: Send seconds.",
        "permanent_link": "♾️ Permanent Link: Toggle.",
        "protect_content": "🔒 Protect Content: Toggle."
    }
    await callback_query.answer(messages.get(key, "Coming soon"), show_alert=True)


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
            "ɪꜰ ɴᴇᴡ ᴜsᴇʀs sᴛᴀʀᴛ ʏᴏᴜʀ ʙᴏᴛ ᴛʜᴇɴ ʙᴏᴛ ɴᴏᴛɪꜰɪᴇs ʏᴏᴜ.\n\n"
            f"✅ **Current Log Channel:** `{log_channel}`"
        )
    else:
        text = (
            "📢 **LOG CHANNEL:**\n\n"
            "ɪꜰ ɴᴇᴡ ᴜsᴇʀs sᴛᴀʀᴛ ʏᴏᴜʀ ʙᴏᴛ ᴛʜᴇɴ ʙᴏᴛ ɴᴏᴛɪꜰɪᴇs ʏᴏᴜ.\n\n"
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
        f"ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ʏᴏᴜʀ ʟᴏɢ ᴄʜᴀɴɴᴇʟ,\n"
        f"ᴀɴᴅ ᴍᴀᴋᴇ sᴜʀᴇ @{bot_username} ɪs ᴀᴅᴍɪɴ ɪɴ ɪᴛ.\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private, group=21)
async def receive_log_channel(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_log_channel":
        return
    if message.text and message.text.startswith("/"):
        edit_states.pop(user_id, None)
        return
    if not message.forward_from_chat:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
        return await message.reply_text("⚠️ Please forward a message from the channel.", reply_markup=InlineKeyboardMarkup(buttons))

    chat = message.forward_from_chat
    chat_type = str(chat.type).lower().replace("chattype.", "")
    if chat_type not in ("channel", "supergroup"):
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
        return await message.reply_text("⚠️ Only channels/supergroups allowed.", reply_markup=InlineKeyboardMarkup(buttons))

    bot_username = (await client.get_me()).username
    try:
        member = await client.get_chat_member(chat.id, "me")
        if member.status not in ("administrator", "creator", "owner"):
            buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
            return await message.reply_text(
                f"⚠️ @{bot_username} is not admin in **{chat.title}**.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
        return await message.reply_text(f"⚠️ Error: `{e}`", reply_markup=InlineKeyboardMarkup(buttons))

    edit_states.pop(user_id, None)
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "log_channel", chat.id)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
    await message.reply_text(f"✅ **Log Channel Set:** {chat.title}", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_delete_log$"))
async def delete_log_channel(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "log_channel", None)
    await callback_query.answer("✅ Deleted.", show_alert=True)
    await log_channel_menu(client, callback_query)


# ==========================================================
# 🔹 DATABASE CHANNEL
# ==========================================================
@Client.on_callback_query(filters.regex("^c_db_channel$"))
async def db_channel_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    db_channel = clone_data.get("db_channel") if clone_data else None

    text = "☁️ **DATABASE CHANNEL:**\n\n"
    if db_channel:
        text += f"✅ **Current:** `{db_channel}`"
    else:
        text += "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ❗️"

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
        f"ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ,\n"
        f"ᴀɴᴅ ᴍᴀᴋᴇ sᴜʀᴇ @{bot_username} ɪs ᴀᴅᴍɪɴ ɪɴ ɪᴛ.\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private, group=22)
async def receive_db_channel(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_db_channel":
        return
    if message.text and message.text.startswith("/"):
        edit_states.pop(user_id, None)
        return
    if not message.forward_from_chat:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
        return await message.reply_text("⚠️ Please forward a message from the channel.", reply_markup=InlineKeyboardMarkup(buttons))

    chat = message.forward_from_chat
    chat_type = str(chat.type).lower().replace("chattype.", "")
    if chat_type not in ("channel", "supergroup"):
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
        return await message.reply_text("⚠️ Only channels/supergroups allowed.", reply_markup=InlineKeyboardMarkup(buttons))

    bot_username = (await client.get_me()).username
    try:
        member = await client.get_chat_member(chat.id, "me")
        if member.status not in ("administrator", "creator", "owner"):
            buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
            return await message.reply_text(
                f"⚠️ @{bot_username} is not admin in **{chat.title}**.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
        return await message.reply_text(f"⚠️ Error: `{e}`", reply_markup=InlineKeyboardMarkup(buttons))

    edit_states.pop(user_id, None)
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "db_channel", chat.id)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
    await message.reply_text(f"✅ **DB Channel Set:** {chat.title}", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_delete_db$"))
async def delete_db_channel(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "db_channel", None)
    await callback_query.answer("✅ Deleted.", show_alert=True)
    await db_channel_menu(client, callback_query)


# ==========================================================
# 🔹 ADMINS
# ==========================================================
@Client.on_callback_query(filters.regex("^c_admins$"))
async def admins_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    admins = clone_data.get("admins", []) if clone_data else []

    text = f"👥 **ADMINS:**\n\n**Total Admins:** {len(admins)}"
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
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await callback_query.message.edit_text("👥 Send user ID to add as admin.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=23)
async def receive_add_admin(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_add_admin":
        return
    try:
        new_admin = int(message.text.strip())
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
        return await message.reply_text("❌ Invalid ID.", reply_markup=InlineKeyboardMarkup(buttons))

    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        admins = clone_data.get("admins", [])
        if new_admin not in admins:
            admins.append(new_admin)
            await db.update_clone_setting(clone_data["user_id"], "admins", admins)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await message.reply_text(f"✅ Admin `{new_admin}` added.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_remove_admin$"))
async def remove_admin_prompt(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    edit_states[user_id] = "waiting_for_remove_admin"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await callback_query.message.edit_text("👥 Send user ID to remove.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=24)
async def receive_remove_admin(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_remove_admin":
        return
    try:
        rem_admin = int(message.text.strip())
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
        return await message.reply_text("❌ Invalid ID.", reply_markup=InlineKeyboardMarkup(buttons))

    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        admins = clone_data.get("admins", [])
        if rem_admin in admins:
            admins.remove(rem_admin)
            await db.update_clone_setting(clone_data["user_id"], "admins", admins)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await message.reply_text(f"✅ Admin `{rem_admin}` removed.", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 BOT STATUS
# ==========================================================
@Client.on_callback_query(filters.regex("^c_status$"))
async def bot_status(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    total_users = await db.users.count_documents({})
    banned_users = await db.banned_users.count_documents({})
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    up = int(time.time() - BOT_START_TIME)
    h, m, s = up // 3600, (up % 3600) // 60, up % 60

    text = (
        f"**{bot_username.upper()}**\n\n"
        f"USERS - {total_users}\n\n"
        f"BAN USERS - {banned_users}\n\n"
        f"CPU - {cpu}%\n\n"
        f"RAM - {ram}%\n\n"
        f"UPTIME - {h} Hours {m} Minutes {s} Seconds"
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
    current = clone_data.get("bot_mode", "public") if clone_data else "public"
    icon = "🌐" if current == "public" else "🔒"

    text = f"🛍️ **BOT MODE**\n\n{icon} Current: {current.title()}"
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
    await callback_query.answer(f"Mode: {mode.title()} ✅", show_alert=True)
    await bot_mode_menu(client, callback_query)


# ==========================================================
# 🔹 RESTART BOT
# ==========================================================
@Client.on_callback_query(filters.regex("^c_restart$"))
async def restart_bot(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("⏱️ Restarting...", show_alert=True)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_settings")]]
    await callback_query.message.edit_text("⏱️ **Restarting bot...**", reply_markup=InlineKeyboardMarkup(buttons))
    asyncio.create_task(_delayed_restart(client))


async def _delayed_restart(client: Client):
    await asyncio.sleep(3)
    try:
        await client.restart()
        print("✅ Restarted.")
    except Exception as e:
        print(f"⚠️ Restart error: {e}")


# ==========================================================
# 🔹 DELETE BOT
# ==========================================================
@Client.on_callback_query(filters.regex("^c_delete_bot$"))
async def delete_bot_prompt(client: Client, callback_query: CallbackQuery):
    text = "🚫 **DELETE BOT**\n\nAre you sure? This cannot be undone."
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
    await callback_query.message.edit_text("✅ Bot deleted.")


# ==========================================================
# 🔹 MORE FEATURES
# ==========================================================
@Client.on_callback_query(filters.regex("^c_more_features$"))
async def more_features(client: Client, callback_query: CallbackQuery):
    text = (
        "🔍 **MORE FEATURES**\n\n"
        "• /settings - User settings\n"
        "• /customize - Clone settings\n"
        "• /broadcast - Broadcast\n"
        "• /ban [id] - Ban\n"
        "• /unban [id] - Unban\n"
        "• /myplan - View plan\n"
        "• /link - Store file\n"
        "• /batch - Store batch"
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
            "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ.\n\n"
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
            [InlineKeyboardButton("Settings", callback_data="c_settings"),
             InlineKeyboardButton("Customize", url=f"https://t.me/{bot_username}?start=customize")],
            [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
             InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
        ]

    await callback_query.message.edit_text(formatted, reply_markup=InlineKeyboardMarkup(buttons if False else keyboard))


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
        return await message.reply_text("❌ Owner only.")
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a message.")

    users = await db.get_all_users()
    status = await message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    success = 0
    for u in users:
        try:
            await message.reply_to_message.copy(u["user_id"])
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await status.edit_text(f"✅ Sent to {success}/{len(users)} users.")

# ==========================================================
# 🔹 /ban and /unban
# ==========================================================
@Client.on_message(filters.command("ban") & filters.private)
async def clone_ban(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if not clone_data or clone_data["user_id"] != user_id:
        return await message.reply_text("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /ban [user_id]")
    try:
        target = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid ID.")
    await db.ban_user(target)
    await message.reply_text(f"✅ User {target} banned.")


@Client.on_message(filters.command("unban") & filters.private)
async def clone_unban(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if not clone_data or clone_data["user_id"] != user_id:
        return await message.reply_text("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /unban [user_id]")
    try:
        target = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid ID.")
    await db.unban_user(target)
    await message.reply_text(f"✅ User {target} unbanned.")

# ==========================================================
# 🔹 VIEW PLANS CALLBACK
# ==========================================================
@Client.on_callback_query(filters.regex("^c_plan$"))
async def c_plan_callback(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    plan_text = await db.get_premium_plan_text(bot_username)

    if not plan_text:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await callback_query.message.edit_text(
            "❌ **Plan Not Available**\n\n"
            "ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ʜᴀs ɴᴏᴛ ʙᴇᴇɴ sᴇᴛ ʏᴇᴛ.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await callback_query.message.edit_text(
        f"💎 **PREMIUM PLAN**\n\n{plan_text}",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )


# ==========================================================
# 🔹 MY PLAN CALLBACK
# ==========================================================
@Client.on_callback_query(filters.regex("^c_myplan$"))
async def c_myplan_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    bot_username = (await client.get_me()).username
    is_premium = await db.is_premium_user(user_id, bot_username)

    if is_premium:
        text = "💎 **My Premium Status**\n\n✅ **Status:** Premium (Active)\n🎁 Unlimited access."
    else:
        text = "💎 **My Premium Status**\n\n📌 **Status:** Free\n🆓 Limit: 5 files/day\n\nType /plan to see plans."

    buttons = [[InlineKeyboardButton("💎 View Plans", callback_data="c_plan")],
               [InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
