# utils/keyboard.py
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================================================
# 🔹 MAIN BOT KEYBOARDS
# ==========================================================

def main_settings_kb():
    """Main bot settings menu keyboard."""
    buttons = [
        [InlineKeyboardButton("💎 PREMIUM PLAN", callback_data="main_premium")],
        [InlineKeyboardButton("🆓 FREE USAGE LIMIT", callback_data="main_free_limit")],
        [InlineKeyboardButton("🌍 REFER AND EARN", callback_data="main_refer")],
        [InlineKeyboardButton("🔗 LINK SHORTNER", callback_data="main_shortner")],
        [InlineKeyboardButton("⏰ TOKEN VERIFICATION", callback_data="main_token_verify")],
        [InlineKeyboardButton("📢 FORCE SUBSCRIBE", callback_data="main_force_sub")],
        [InlineKeyboardButton("🍿 CAPTION", callback_data="main_caption"),
         InlineKeyboardButton("🖼️ THUMBNAIL", callback_data="main_thumbnail")],
        [InlineKeyboardButton("⚪ BUTTON", callback_data="main_button"),
         InlineKeyboardButton("♻️ AUTO DELETE", callback_data="main_auto_delete")],
        [InlineKeyboardButton("♾️ PERMANENT LINK", callback_data="main_permanent_link")],
        [InlineKeyboardButton("🔒 PROTECT CONTENT", callback_data="main_protect_content")],
        [InlineKeyboardButton("🔙 BACK", callback_data="main_back")]
    ]
    return InlineKeyboardMarkup(buttons)


def caption_menu_kb():
    buttons = [
        [InlineKeyboardButton("Set Caption", callback_data="main_set_caption")],
        [InlineKeyboardButton("Default Caption", callback_data="main_default_caption")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_settings")]
    ]
    return InlineKeyboardMarkup(buttons)


def button_menu_kb(has_buttons: bool):
    if has_buttons:
        buttons = [
            [InlineKeyboardButton("See Buttons", callback_data="main_see_buttons")],
            [InlineKeyboardButton("Remove Buttons", callback_data="main_remove_buttons")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_settings")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton("Add Buttons", callback_data="main_add_buttons")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_settings")]
        ]
    return InlineKeyboardMarkup(buttons)


def thumbnail_menu_kb():
    buttons = [
        [InlineKeyboardButton("Set Thumbnail", callback_data="main_set_thumb"),
         InlineKeyboardButton("View Thumbnail", callback_data="main_view_thumb")],
        [InlineKeyboardButton("Remove Thumbnail", callback_data="main_remove_thumb")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_settings")]
    ]
    return InlineKeyboardMarkup(buttons)


# ==========================================================
# 🔹 CLONE BOT KEYBOARDS
# ==========================================================

def clone_settings_kb():
    """Clone bot settings menu keyboard."""
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
    return InlineKeyboardMarkup(buttons)


def clone_menu_kb():
    """Clone owner menu keyboard."""
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
    return InlineKeyboardMarkup(buttons)
