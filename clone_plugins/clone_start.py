# clone_plugins/clone_start.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import asyncio


# ==========================================================
# 🔹 /start
# ==========================================================
@Client.on_message(filters.command("start") & filters.private)
async def clone_start(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    bot_mention = f"@{bot_username}"
    user_mention = message.from_user.mention

    # Deep link handling (unchanged)
    if len(message.command) > 1:
        payload = message.command[1]
        if payload == "customize":
            clone_data = await db.get_clone_by_username(bot_username)
            if clone_data and clone_data["user_id"] == user_id:
                await send_clone_settings(message)
                return
        stored = await db.get_stored_file(payload)
        if stored:
            # ... (file sending logic)
            return

    # Load custom start text/pic/buttons
    clone_data = await db.get_clone_by_username(bot_username)
    start_text = clone_data.get("start_text") if clone_data else None
    start_pic = clone_data.get("start_pic") if clone_data else None
    start_buttons = clone_data.get("start_buttons", []) if clone_data else []

    # Default text if none set
    if not start_text:
        start_text = (
            "ʜᴇʏ {mention} 👋,\n\n"
            "ᴍʏ ɴᴀᴍᴇ ɪs {bot_mention}\n\n"
            "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴀɴᴅ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss sᴛᴏʀᴇᴅ ᴍᴇssᴀɢᴇs ʙʏ ᴜsɪɴɢ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɢɪᴠᴇɴ ʙʏ ᴍᴇ.\n\n"
            "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
        )

    # Replace placeholders
    formatted_text = start_text.format(mention=user_mention, bot_mention=bot_mention)

    # Build inline keyboard from stored buttons
    keyboard = []
    for btn in start_buttons:
        keyboard.append([InlineKeyboardButton(btn["text"], url=btn["url"])])

    # Add default Help/About buttons if none are set
    if not keyboard:
        keyboard = [
            [InlineKeyboardButton("Help", callback_data="c_help"),
             InlineKeyboardButton("About", callback_data="c_about")],
            [InlineKeyboardButton("Settings", callback_data="c_settings")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send with picture or text
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
        [InlineKeyboardButton("💰 MONETIZATION", callback_data="c_monetization")],
        [InlineKeyboardButton("📝 START MESSAGE", callback_data="c_start_msg")],
        [InlineKeyboardButton("📢 LOG CHANNEL", callback_data="c_log_channel")],
        [InlineKeyboardButton("☁️ DATABASE CHANNEL", callback_data="c_db_channel")],
        [InlineKeyboardButton("👥 ADMINS", callback_data="c_admins")],
        [InlineKeyboardButton("📊 BOT STATUS", callback_data="c_status")],
        [InlineKeyboardButton("🛍️ BOT MODE", callback_data="c_bot_mode")],
        [InlineKeyboardButton("⏱️ RESTART BOT", callback_data="c_restart")],
        [InlineKeyboardButton("🚫 DELETE BOT", callback_data="c_delete_bot")],
        [InlineKeyboardButton("🔍 MORE FEATURES", callback_data="c_more_features")],
        [InlineKeyboardButton("🔙 BACK", callback_data="c_back")]
    ]
    if edit:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 SETTINGS BUTTON HANDLERS
# ==========================================================
@Client.on_callback_query(filters.regex("^c_(monetization|start_msg|log_channel|db_channel|admins|status|bot_mode|restart|delete_bot|more_features)$"))
async def settings_button_handler(client: Client, callback_query: CallbackQuery):
    key = callback_query.data.replace("c_", "")
    messages = {
        "monetization": "💰 MONETIZATION\n\nConfigure shortlink API and earnings.",
        "start_msg": "📝 START MESSAGE\n\nSend me the message to display on /start.",
        "log_channel": "📢 LOG CHANNEL\n\nForward a message from your log channel.",
        "db_channel": "☁️ DATABASE CHANNEL\n\nForward a message from your DB channel.",
        "admins": "👥 ADMINS\n\nSend me user IDs (one per line) to promote.",
        "status": "📊 BOT STATUS\n\nYour clone bot is running normally.",
        "bot_mode": "🛍️ BOT MODE\n\nChoose: Public / Private / Approval.",
        "restart": "⏱️ RESTART BOT\n\nSend /restart_confirm to restart.",
        "delete_bot": "🚫 DELETE BOT\n\nSend /delete_confirm to permanently delete.",
        "more_features": "🔍 MORE FEATURES\n\nComing soon!"
    }
    await callback_query.answer(messages.get(key, "Coming soon"), show_alert=True)


# ==========================================================
# 🔹 BACK
# ==========================================================
@Client.on_callback_query(filters.regex("^c_back$"))
async def clone_back_cb(client: Client, callback_query: CallbackQuery):
    first_name = callback_query.from_user.first_name
    text = (
        f"ʜᴇʏ {first_name} 👋,\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴡɪᴛʜ ᴄʟᴏɴᴇ ᴀɴᴅ ᴍᴀɴʏ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇ ᴀɴᴅ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss sᴛᴏʀᴇᴅ ᴍᴇssᴀɢᴇs ʙʏ ᴜsɪɴɢ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɢɪᴠᴇɴ ʙʏ ᴍᴇ\n\n"
        "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
    )
    buttons = [
        [InlineKeyboardButton("Help", callback_data="c_help"),
         InlineKeyboardButton("About", callback_data="c_about")],
        [InlineKeyboardButton("Settings", callback_data="c_settings")],
        [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
         InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


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
# 🔹 /ban and /unban (CORRECTED)
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
