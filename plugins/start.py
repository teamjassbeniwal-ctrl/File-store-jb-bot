# plugins/start.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from config import OWNER_ID

# ==========================================================
# 🔹 /start COMMAND
# ==========================================================
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    await db.add_user(user_id)

    clone = await db.get_clone(user_id)

    text = (
        f"ʜᴇʏ {first_name} 👋,\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴡɪᴛʜ ᴄʟᴏɴᴇ ᴀɴᴅ ᴍᴀɴʏ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇ ᴀɴᴅ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss sᴛᴏʀᴇᴅ ᴍᴇssᴀɢᴇs ʙʏ ᴜsɪɴɢ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɢɪᴠᴇɴ ʙʏ ᴍᴇ\n\n"
        "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
    )

    buttons = [
        [
            InlineKeyboardButton("Help", callback_data="main_help"),
            InlineKeyboardButton("About", callback_data="main_about")
        ],
        [
            InlineKeyboardButton("Create Own Clone", callback_data="create_clone")
        ],
        [
            InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
            InlineKeyboardButton("Support", url="https://t.me/YourSupport")
        ]
    ]

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 /help COMMAND
# ==========================================================
@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
    await send_help_menu(message)


@Client.on_callback_query(filters.regex("main_help"))
async def help_callback(client: Client, callback_query: CallbackQuery):
    await send_help_menu(callback_query.message, edit=True)


async def send_help_menu(message, edit=False):
    help_text = (
        "🎓 **HELP MENU:**\n\n"
        "🤖 ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ\n"
        "📨 ᴍʏ ɴᴀᴍᴇ ɪꜱ ꜰɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ʙᴜᴛ ɪ ᴄᴀɴ ꜱᴛᴏʀᴇ ᴀɴʏ ᴛʏᴘᴇ ᴏꜰ ᴄᴏɴᴛᴇɴᴛ, ɪɴᴄʟᴜᴅɪɴɢ ᴍᴇꜱꜱᴀɢᴇꜱ, ᴘʜᴏᴛᴏꜱ, ᴠɪᴅᴇᴏꜱ, ᴀɴᴅ ꜰɪʟᴇꜱ.\n"
        "📂 ʏᴏᴜ ᴄᴀɴ ꜱᴛᴏʀᴇ ꜰɪʟᴇꜱ ꜰʀᴏᴍ ʏᴏᴜʀ ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴅɪɴɢ ᴍᴇ ᴀꜱ ᴀɴ ᴀᴅᴍɪɴ.\n"
        "🔐 ɪꜰ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴏʀ ɢʀᴏᴜᴘ ɪꜱ ᴘʀɪᴠᴀᴛᴇ, ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ꜰɪʀꜱᴛ.\n"
        "🔗 ᴀꜰᴛᴇʀ ꜱᴛᴏʀɪɴɢ, ɪ ᴡɪʟʟ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ꜰᴏʀ ɪɴꜱᴛᴀɴᴛ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ʏᴏᴜʀ ꜱᴛᴏʀᴇᴅ ᴄᴏɴᴛᴇɴᴛ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "📚 **BASIC COMMANDS**\n\n"
        "➤ /start - ᴄʜᴇᴄᴋ ɪꜰ ɪ'ᴍ ᴀʟɪᴠᴇ.\n"
        "➤ /id - ɢᴇᴛ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "📦 **FILE STORAGE COMMANDS**\n\n"
        "➤ /link - ꜱᴛᴏʀᴇ ᴀ ꜱɪɴɢʟᴇ ꜰɪʟᴇ ᴏʀ ᴍᴇꜱꜱᴀɢᴇ.\n"
        "➤ /batch - ꜱᴛᴏʀᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴄᴏɴꜱᴇᴄᴜᴛɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.\n"
        "➤ /custom_batch - ꜱᴛᴏʀᴇ ᴍᴜʟᴛɪᴘʟᴇ ʀᴀɴᴅᴏᴍ ᴍᴇꜱꜱᴀɢᴇꜱ.\n"
        "➤ /multiple_batch - ᴄʀᴇᴀᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ʙᴀᴛᴄʜ ʟɪɴᴋꜱ ᴀᴛ ᴏɴᴄᴇ.\n"
        "➤ /special_link - ᴄʀᴇᴀᴛᴇ ꜱᴘᴇᴄɪᴀʟ ʟɪɴᴋꜱ ᴡɪᴛʜ ᴄᴜꜱᴛᴏᴍ ꜱᴇᴛᴛɪɴɢꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "💎 **PREMIUM COMMANDS**\n\n"
        "➤ /myplan - ᴠɪᴇᴡ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴅᴇᴛᴀɪʟꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "🤖 **CLONE BOT COMMANDS**\n\n"
        "➤ /clone - ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ.\n"
        "➤ /activate - ᴀᴄᴛɪᴠᴀᴛᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ.\n"
        "➤ /delete - ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "⚙️ **USER SETTINGS**\n\n"
        "➤ /settings - ᴄᴜꜱᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ ᴘᴇʀꜱᴏɴᴀʟ ꜱᴇᴛᴛɪɴɢꜱ.\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "👑 **ADMIN COMMANDS**\n\n"
        "➤ /broadcast - ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ (ᴏᴡɴᴇʀ ᴏɴʟʏ)."
    )
    buttons = [
        [InlineKeyboardButton("Settings", callback_data="main_settings"),
         InlineKeyboardButton("About", callback_data="main_about")],
        [InlineKeyboardButton("Back", callback_data="main_back")]
    ]
    if edit:
        await message.edit_text(help_text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(help_text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 /about COMMAND
# ==========================================================
@Client.on_message(filters.command("about") & filters.private)
async def about_cmd(client: Client, message: Message):
    await send_about_menu(message)


@Client.on_callback_query(filters.regex("main_about"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    await send_about_menu(callback_query.message, edit=True)


async def send_about_menu(message, edit=False):
    about_text = (
        "○ **Creator** : King VJ\n"
        "○ **Language** : Python3\n"
        "○ **Library** : Pyrogram 2.0.106\n"
        "○ **Channel** : @teamjb1\n"
        "○ **Support Group** : @jbsupportgroup"
    )
    buttons = [
        [InlineKeyboardButton("Settings", callback_data="main_settings"),
         InlineKeyboardButton("Help", callback_data="main_help")],
        [InlineKeyboardButton("Back", callback_data="main_back")]
    ]
    if edit:
        await message.edit_text(about_text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(about_text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 /id COMMAND
# ==========================================================
@Client.on_message(filters.command("id") & filters.private)
async def id_cmd(client: Client, message: Message):
    user = message.from_user
    premium_status = "True" if user.is_premium else "False"
    first_name = user.first_name if user.first_name else "None"
    last_name = user.last_name if user.last_name else "None"
    username = f"@{user.username}" if user.username else "None"
    mention = user.mention if user.username else first_name

    text = (
        "User Details :\n\n\n"
        f"🦚 **First Name** : {first_name}\n\n"
        f"🐧 **Last Name** : {last_name}\n\n"
        f"👤 **User Id** : `{user.id}`\n\n"
        f"👦 **Username** : {username}\n\n"
        f"🔗 **User Link** : {mention}\n\n"
        f"🌟 **Telegram Premium** : {premium_status}\n\n"
        f"📃 **Language Code** : {user.language_code}\n\n"
        "💫 **Status** : Recently\n\n"
        "If you need user id, Then just tap and copy."
    )
    await message.reply_text(text)


# ==========================================================
# 🔹 /settings COMMAND (Image 2 - Main Settings Menu)
# ==========================================================
@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client: Client, message: Message):
    await send_main_settings(message)


@Client.on_callback_query(filters.regex("main_settings"))
async def settings_callback(client: Client, callback_query: CallbackQuery):
    await send_main_settings(callback_query.message, edit=True)


async def send_main_settings(message, edit=False):
    text = (
        "HERE IS THE SETTINGS MENU\n\n"
        "CUSTOMIZE YOUR SETTINGS AS PER YOUR NEED"
    )
    buttons = [
        [InlineKeyboardButton("🤖 MY CLONE BOT", callback_data="create_clone")],
        [InlineKeyboardButton("💎 PREMIUM PLAN", callback_data="premium")]
        [InlineKeyboardButton("🔗 LINK SHORTNER", callback_data="shortner")],
        [InlineKeyboardButton("⏰ TOKEN VERIFICATION", callback_data="token_verify")],
        [InlineKeyboardButton("🍿 CUSTOM CAPTION", callback_data="custom_caption")],
        [InlineKeyboardButton("📢 CUSTOM FORCE SUBSCRIBE", callback_data="custom_force_sub")],
        [InlineKeyboardButton("⚪ CUSTOM BUTTON", callback_data="custom_button")],
        [InlineKeyboardButton("♻️ AUTO DELETE", callback_data="auto_delete")],
        [InlineKeyboardButton("🔒 PROTECT CONTENT", callback_data="protect_content")],
        [InlineKeyboardButton("🔙 BACK", callback_data="main_back")]
    ]
    if edit:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 BACK TO MAIN CALLBACK
# ==========================================================
@Client.on_callback_query(filters.regex("main_back"))
async def back_callback(client: Client, callback_query: CallbackQuery):
    first_name = callback_query.from_user.first_name
    text = (
        f"ʜᴇʏ {first_name} 👋,\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴡɪᴛʜ ᴄʟᴏɴᴇ ᴀɴᴅ ᴍᴀɴʏ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇ ᴀɴᴅ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss sᴛᴏʀᴇᴅ ᴍᴇssᴀɢᴇs ʙʏ ᴜsɪɴɢ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɢɪᴠᴇɴ ʙʏ ᴍᴇ\n\n"
        "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
    )
    buttons = [
        [InlineKeyboardButton("Help", callback_data="main_help"),
         InlineKeyboardButton("About", callback_data="main_about")],
        [InlineKeyboardButton("Create Own Clone", callback_data="create_clone")],
        [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
         InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
