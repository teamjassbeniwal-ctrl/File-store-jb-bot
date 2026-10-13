from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Image 2: Main Settings Menu
def main_settings_kb(user_id):
    buttons = [
        [InlineKeyboardButton("🤖 MY CLONE BOT", callback_data="my_clone")],
        [InlineKeyboardButton("💎 PREMIUM PLAN", callback_data="premium")],
        [InlineKeyboardButton("🔗 LINK SHORTNER", callback_data="shortner")],
        [InlineKeyboardButton("⏰ TOKEN VERIFICATION", callback_data="token_verify")],
        [InlineKeyboardButton("🍿 CUSTOM CAPTION", callback_data="custom_caption")],
        [InlineKeyboardButton("📢 CUSTOM FORCE SUBSCRIBE", callback_data="custom_force_sub")],
        [InlineKeyboardButton("⚪ CUSTOM BUTTON", callback_data="custom_button")],
        [InlineKeyboardButton("♻️ AUTO DELETE", callback_data="auto_delete")],
        [InlineKeyboardButton("🔒 PROTECT CONTENT", callback_data="protect_content")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_main")]
    ]
    return InlineKeyboardMarkup(buttons)

# Image 6: Clone Bot Settings (Only for clone owner)
def clone_settings_kb(clone_username):
    buttons = [
        [InlineKeyboardButton("💰 MONETIZATION", callback_data="monetization")],
        [InlineKeyboardButton("📝 START MESSAGE", callback_data="start_msg")],
        [InlineKeyboardButton("📢 LOG CHANNEL", callback_data="log_channel")],
        [InlineKeyboardButton("☁️ DATABASE CHANNEL", callback_data="db_channel")],
        [InlineKeyboardButton("👥 ADMINS", callback_data="admins")],
        [InlineKeyboardButton("📊 BOT STATUS", callback_data="status")],
        [InlineKeyboardButton("🛍️ BOT MODE", callback_data="bot_mode")],
        [InlineKeyboardButton("⏱️ RESTART BOT", callback_data="restart")],
        [InlineKeyboardButton("🚫 DELETE BOT", callback_data="delete_bot")],
        [InlineKeyboardButton("🔍 MORE FEATURES", callback_data="more_features")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_clone")]
    ]
    return InlineKeyboardMarkup(buttons)

# Image 8: User Settings
def user_settings_kb():
    buttons = [
        [InlineKeyboardButton("💎 PREMIUM PLAN", callback_data="premium")],
        [InlineKeyboardButton("🆓 FREE USAGE LIMIT", callback_data="free_limit")],
        [InlineKeyboardButton("🌍 REFER AND EARN", callback_data="refer")],
        [InlineKeyboardButton("🔗 LINK SHORTNER", callback_data="shortner")],
        [InlineKeyboardButton("⏰ TOKEN VERIFICATION", callback_data="token_verify")],
        [InlineKeyboardButton("📢 FORCE SUBSCRIBE", callback_data="force_sub")],
        [InlineKeyboardButton("🍿 CAPTION", callback_data="caption")],
        [InlineKeyboardButton("🖼️ THUMBNAIL", callback_data="thumbnail")],
        [InlineKeyboardButton("⚪ BUTTON", callback_data="button")],
        [InlineKeyboardButton("♻️ AUTO DELETE", callback_data="auto_delete")],
        [InlineKeyboardButton("♾️ PERMANENT LINK", callback_data="permanent_link")],
        [InlineKeyboardButton("🔒 PROTECT CONTENT", callback_data="protect_content")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back")]
    ]
    return InlineKeyboardMarkup(buttons)
