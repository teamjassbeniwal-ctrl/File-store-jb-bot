# clone_plugins/clone_start.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import asyncio

# 🔹 CLONE BOT START
@Client.on_message(filters.command("start") & filters.private)
async def clone_start(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    bot_username = (await client.get_me()).username

    if len(message.command) > 1:
        payload = message.command[1]
        if payload == "customize":
            clone_data = await db.get_clone_by_username(bot_username)
            if clone_data and clone_data["user_id"] == user_id:
                await send_clone_settings(client, message)
                return
        stored = await db.get_stored_file(payload)
        if stored:
            await message.reply_cached_media(stored["file_id"], caption="📁 **Here is your file**")
            return

    text = (
        f"ʜᴇʏ {first_name} 👋,\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴡɪᴛʜ ᴄʟᴏɴᴇ ᴀɴᴅ ᴍᴀɴʏ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs.\n\n"
        "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
    )
    buttons = [
        [InlineKeyboardButton("Help", callback_data="c_help"),
         InlineKeyboardButton("About", callback_data="c_about")],
        [InlineKeyboardButton("Settings", callback_data="c_settings")],
        [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
         InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# 🔹 CLONE HELP
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
        "📨 ᴍʏ ɴᴀᴍᴇ ɪꜱ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ, ʙᴜᴛ ɪ ᴄᴀɴ ꜱᴛᴏʀᴇ ᴀɴʏ ᴛʏᴘᴇ ᴏꜰ ᴄᴏɴᴛᴇɴᴛ, ɪɴᴄʟᴜᴅɪɴɢ ᴍᴇꜱꜱᴀɢᴇꜱ, ᴘʜᴏᴛᴏꜱ, ᴠɪᴅᴇᴏꜱ, ᴀɴᴅ ꜰɪʟᴇꜱ.\n"
        "📂 ʏᴏᴜ ᴄᴀɴ ꜱᴛᴏʀᴇ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ʏᴏᴜʀ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴅɪɴɢ ᴍᴇ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ.\n"
        "🔐 ɪꜰ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴏʀ ɢʀᴏᴜᴘ ɪꜱ ᴘʀɪᴠᴀᴛᴇ, ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ꜰɪʀꜱᴛ.\n"
        "🔗 ᴀꜰᴛᴇʀ ꜱᴛᴏʀɪɴɢ, ɪ ᴡɪʟʟ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ꜰᴏʀ ɪɴꜱᴛᴀɴᴛ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ʏᴏᴜʀ ꜰɪʟᴇꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "📚 **BASIC COMMANDS**\n\n"
        "➤ /start - ᴄʜᴇᴄᴋ ɪꜰ ɪ'ᴍ ᴀʟɪᴠᴇ.\n"
        "➤ /id - ɢᴇᴛ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ.\n\n"
        "📦 **FILE STORAGE COMMANDS**\n\n"
        "➤ /link - ꜱᴛᴏʀᴇ ᴀ ꜱɪɴɢʟᴇ ꜰɪʟᴇ ᴏʀ ᴍᴇꜱꜱᴀɢᴇ.\n"
        "➤ /batch - ꜱᴛᴏʀᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴄᴏɴꜱᴇᴄᴜᴛɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ ꜰʀᴏᴍ ᴀ ᴄʜᴀɴɴᴇʟ.\n"
        "➤ /custom_batch - ꜱᴛᴏʀᴇ ᴍᴜʟᴛɪᴘʟᴇ ʀᴀɴᴅᴏᴍ ᴍᴇꜱꜱᴀɢᴇꜱ.\n"
        "➤ /multiple_batch - ᴄʀᴇᴀᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ʙᴀᴛᴄʜ ʟɪɴᴋꜱ ᴀᴛ ᴏɴᴄᴇ.\n"
        "➤ /special_link - ᴄʀᴇᴀᴛᴇ ꜱᴘᴇᴄɪᴀʟ ʟɪɴᴋꜱ ᴡɪᴛʜ ᴄᴜꜱᴛᴏᴍ ꜱᴇᴛᴛɪɴɢꜱ.\n\n"
        "💎 **PREMIUM COMMANDS**\n\n"
        "➤ /createcode - ᴄʀᴇᴀᴛᴇ ᴘʀᴇᴍɪᴜᴍ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇꜱ.\n"
        "➤ /redeem - ʀᴇᴅᴇᴇᴍ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴄᴏᴅᴇ.\n"
        "➤ /myplan - ᴠɪᴇᴡ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴅᴇᴛᴀɪʟꜱ.\n\n"
        "⚙️ **USER SETTINGS**\n\n"
        "➤ /settings - ᴄᴜꜱᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ꜱᴇᴛᴛɪɴɢꜱ.\n\n"
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


# 🔹 CLONE ABOUT
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


# 🔹 CLONE /id COMMAND
@Client.on_message(filters.command("id") & filters.private)
async def clone_id_cmd(client: Client, message: Message):
    user = message.from_user
    premium_status = "True" if user.is_premium else "False"
    text = (
        "User Details :\n\n\n"
        f"🦚 **First Name** : {user.first_name}\n\n"
        f"🐧 **Last Name** : {user.last_name or 'None'}\n\n"
        f"👤 **User Id** : `{user.id}`\n\n"
        f"👦 **Username** : @{user.username or 'None'}\n\n"
        f"🔗 **User Link** : {user.mention}\n\n"
        f"🌟 **Telegram Premium** : {premium_status}\n\n"
        f"📃 **Language Code** : {user.language_code}\n\n"
        "💫 **Status** : Recently"
    )
    await message.reply_text(text)


# 🔹 CLONE SETTINGS MENU
async def send_clone_settings(client: Client, message: Message):
    text = "⚙️ **CLONE BOT SETTINGS**\n\nCustomize your bot:"
    buttons = [
        [InlineKeyboardButton("💰 MONETIZATION", callback_data="c_monetization")],
        [InlineKeyboardButton("📝 START MESSAGE", callback_data="c_start_msg")],
        [InlineKeyboardButton("📢 LOG CHANNEL", callback_data="c_log_channel")],
        [InlineKeyboardButton("☁️ DATABASE CHANNEL", callback_data="c_db_channel")],
        [InlineKeyboardButton("👥 ADMINS", callback_data="c_admins")],
        [InlineKeyboardButton("📊 BOT STATUS", callback_data="c_status")],
        [InlineKeyboardButton("🔙 BACK", callback_data="c_back")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# 🔹 CLONE BACK
@Client.on_callback_query(filters.regex("^c_back$"))
async def clone_back_cb(client: Client, callback_query: CallbackQuery):
    first_name = callback_query.from_user.first_name
    text = (
        f"ʜᴇʏ {first_name} 👋,\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴡɪᴛʜ ᴄʟᴏɴᴇ ᴀɴᴅ ᴍᴀɴʏ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇs.\n\n"
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


# 🔹 CLONE BROADCAST
@Client.on_message(filters.command("broadcast") & filters.private)
async def clone_broadcast(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != user_id:
        return await message.reply_text("❌ **Owner only command.**")

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

    await status.edit_text(f"✅ Broadcast complete! Sent to {success}/{len(users)} users.")
