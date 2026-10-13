# clone_plugins/clone_start.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import db

# 🔹 START COMMAND FOR CLONE BOT
@Client.on_message(filters.command("start") & filters.private)
async def clone_start(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    
    # Check if the command is a deep link (e.g., /start customize or /start file_id)
    if len(message.command) > 1:
        payload = message.command[1]
        
        # Customize menu (Image 6) - Only for the clone owner
        if payload == "customize":
            clone_data = await db.clones.find_one({"bot_username": bot_username})
            if clone_data and clone_data['user_id'] == user_id:
                await send_clone_settings(client, message)
                return
            else:
                await message.reply_text("⚠️ Only the bot owner can customize this bot.")
                return
        
        # Otherwise, treat payload as a file unique_id
        file_data = await db.get_file(payload)
        if file_data:
            await message.reply_cached_media(
                file_data['file_id'],
                caption=f"📁 **Here is your file**\n\n🔗 Requested by: {message.from_user.mention}"
            )
            return
        else:
            await message.reply_text("❌ Invalid or expired link.")
            return

    # Normal /start - Show welcome message
    buttons = [
        [InlineKeyboardButton("📢 Channel", url="https://t.me/YourChannel")],
        [InlineKeyboardButton("💬 Support", url="https://t.me/YourSupport")]
    ]
    await message.reply_text(
        f"👋 **Hello {message.from_user.first_name}!**\n\n"
        "I am a File Store Bot. Send me any file and I will give you a shareable link.\n\n"
        "Use /help to see all commands.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# 🔹 SEND CLONE SETTINGS MENU (Image 6)
async def send_clone_settings(client: Client, message: Message):
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
    text = (
        "🛠️ **CLONE MENU**\n\n"
        "**WELCOME TO YOUR CLONE BOT MANAGEMENT HUB!**\n"
        "Customize your bot settings or manage its status using the options below.\n\n"
        "⚙️ **QUICK COMMANDS**\n"
        "🚀 /activate — Activate your clone bot\n"
        "🗑️ /delete — Permanently delete your clone bot"
    )
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# 🔹 SETTINGS COMMAND (Image 8 - User Settings)
@Client.on_message(filters.command("settings") & filters.private)
async def user_settings(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("💎 PREMIUM PLAN", callback_data="u_premium")],
        [InlineKeyboardButton("🆓 FREE USAGE LIMIT", callback_data="u_free_limit")],
        [InlineKeyboardButton("🌍 REFER AND EARN", callback_data="u_refer")],
        [InlineKeyboardButton("🔗 LINK SHORTNER", callback_data="u_shortner")],
        [InlineKeyboardButton("⏰ TOKEN VERIFICATION", callback_data="u_token_verify")],
        [InlineKeyboardButton("📢 FORCE SUBSCRIBE", callback_data="u_force_sub")],
        [InlineKeyboardButton("🍿 CAPTION", callback_data="u_caption")],
        [InlineKeyboardButton("🖼️ THUMBNAIL", callback_data="u_thumbnail")],
        [InlineKeyboardButton("⚪ BUTTON", callback_data="u_button")],
        [InlineKeyboardButton("♻️ AUTO DELETE", callback_data="u_auto_delete")],
        [InlineKeyboardButton("♾️ PERMANENT LINK", callback_data="u_permanent_link")],
        [InlineKeyboardButton("🔒 PROTECT CONTENT", callback_data="u_protect_content")],
        [InlineKeyboardButton("🔙 BACK", callback_data="u_back")]
    ]
    await message.reply_text(
        "⚙️ **USER SETTINGS**\n\nCustomize your personal settings:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# 🔹 CALLBACK HANDLER FOR ALL CLONE BUTTONS
@Client.on_callback_query()
async def clone_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    # --- Clone Owner Settings ---
    if data == "c_start_msg":
        await callback_query.message.edit_text(
            "📝 **START MESSAGE**\n\nSend me the new start message for your bot.\n\n"
            "Type /cancel to cancel."
        )
        # Store state in DB (simplified - you need a state machine)
    
    elif data == "c_delete_bot":
        await callback_query.message.edit_text(
            "🚫 **DELETE BOT**\n\nAre you sure? This will permanently delete your clone bot.\n\n"
            "Send `/confirm_delete` to confirm.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="c_back")]
            ])
        )
    
    elif data == "c_back":
        await send_clone_settings(client, callback_query.message)
    
    # --- User Settings ---
    elif data == "u_caption":
        await callback_query.message.edit_text(
            "🍿 **CAPTION SETTINGS**\n\nSend me the caption text you want to use for your files."
        )
    
    elif data == "u_thumbnail":
        await callback_query.message.edit_text(
            "🖼️ **THUMBNAIL SETTINGS**\n\nSend me a photo to set as your thumbnail."
        )
    
    elif data == "u_auto_delete":
        await callback_query.message.edit_text(
            "♻️ **AUTO DELETE**\n\nSend me the time in seconds (e.g., 300 for 5 minutes)."
        )
    
    elif data == "u_back":
        await user_settings(client, callback_query.message)
    
    else:
        await callback_query.answer("⚙️ This feature is coming soon!", show_alert=True)
