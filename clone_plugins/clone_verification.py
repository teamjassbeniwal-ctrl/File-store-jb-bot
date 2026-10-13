# clone_plugins/clone_verification.py
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from database import db
import time

vv_states = {}


async def safe_edit(message, text, markup=None):
    try:
        await message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    except MessageNotModified:
        pass
    except Exception as e:
        print(f"Edit error: {e}")


# ==========================================================
# 🔹 MAIN TOKEN VERIFICATION MENU
# ==========================================================
@Client.on_callback_query(filters.regex("^u_token_verify$"))
async def token_verify_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    status = await db.get_verify_status(bot_username)
    on_off = "ON ✅" if status else "OFF ❌"

    text = (
        "ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴛᴏᴋᴇɴ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ sᴇᴛᴛɪɴɢs "
        "ғʀᴏᴍ ʜᴇʀᴇ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs"
    )

    buttons = [
        [InlineKeyboardButton("Verify Shortner", callback_data="cv_verify_sl"),
         InlineKeyboardButton("Verify Tutorial", callback_data="cv_verify_tt")],
        [InlineKeyboardButton("Verify Time", callback_data="cv_verify_time"),
         InlineKeyboardButton("Second Verification", callback_data="cv_second")],
        [InlineKeyboardButton("Third Verification", callback_data="cv_third")],
        [InlineKeyboardButton(f"Verify On/Off: {on_off}", callback_data="cv_toggle")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 VERIFY SHORTLINK
# ==========================================================
@Client.on_callback_query(filters.regex("^cv_verify_sl$"))
async def verify_shortlink_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    url = await db.get_verify_shortlink_url(bot_username)
    api = await db.get_verify_shortlink_api(bot_username)

    if url:
        text = (
            "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ᴠᴇʀɪғʏ sʜᴏʀᴛʟɪɴᴋ\n\n"
            f"ᴜʀʟ - {url}\n"
            f"ᴀᴘɪ - {api or 'Not set'}"
        )
    else:
        text = (
            "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ᴠᴇʀɪғʏ sʜᴏʀᴛʟɪɴᴋ\n\n"
            "ᴜʀʟ - Not set\nᴀᴘɪ - Not set"
        )

    buttons = [
        [InlineKeyboardButton("Set Shortlink", callback_data="cv_sl_set")],
        [InlineKeyboardButton("Delete Shortlink", callback_data="cv_sl_del")],
        [InlineKeyboardButton("🔙 Back", callback_data="u_token_verify")]
    ]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^cv_sl_set$"))
async def verify_sl_set(client: Client, callback_query: CallbackQuery):
    vv_states[callback_query.from_user.id] = "waiting_verify_sl_url"
    text = (
        "sᴇɴᴅ ᴍᴇ ᴀ sʜᴏʀᴛʟɪɴᴋ ᴜʀʟ...\n\n"
        "ғᴏʀᴍᴀᴛ :\n\n"
        "https://vjlink.online - ❌\n\n"
        "vjlink.online - ✅\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="cv_verify_sl")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^cv_sl_del$"))
async def verify_sl_del(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_verify_shortlink(bot_username)
    await callback_query.answer("✅ Deleted.", show_alert=True)
    await verify_shortlink_menu(client, callback_query)


# ==========================================================
# 🔹 VERIFY TUTORIAL
# ==========================================================
@Client.on_callback_query(filters.regex("^cv_verify_tt$"))
async def verify_tutorial_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    link = await db.get_verify_tutorial(bot_username)

    text = (
        "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ "
        "sʜᴏʀᴛɴᴇʀ ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ ʟɪɴᴋ ꜰᴏʀ ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ.\n\n"
        f"ʟɪɴᴋ - {link or 'Not set'}"
    )

    buttons = [
        [InlineKeyboardButton("Set Tutorial", callback_data="cv_tt_set")],
        [InlineKeyboardButton("Delete Tutorial", callback_data="cv_tt_del")],
        [InlineKeyboardButton("🔙 Back", callback_data="u_token_verify")]
    ]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^cv_tt_set$"))
async def verify_tt_set(client: Client, callback_query: CallbackQuery):
    vv_states[callback_query.from_user.id] = "waiting_verify_tt"
    text = (
        "sᴇɴᴅ ᴍᴇ ᴀ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ...\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="cv_verify_tt")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^cv_tt_del$"))
async def verify_tt_del(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_verify_tutorial(bot_username)
    await callback_query.answer("✅ Deleted.", show_alert=True)
    await verify_tutorial_menu(client, callback_query)


# ==========================================================
# 🔹 VERIFY TIME
# ==========================================================
@Client.on_callback_query(filters.regex("^cv_verify_time$"))
async def verify_time_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    t = await db.get_verify_time(bot_username)

    text = (
        "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴛɪᴍᴇ sᴇᴛᴛɪɴɢ.\n\n"
        f"ᴛɪᴍᴇ - {t}"
    )

    buttons = [
        [InlineKeyboardButton("Set Time", callback_data="cv_time_set")],
        [InlineKeyboardButton("🔙 Back", callback_data="u_token_verify")]
    ]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^cv_time_set$"))
async def verify_time_set(client: Client, callback_query: CallbackQuery):
    vv_states[callback_query.from_user.id] = "waiting_verify_time"
    text = (
        "sᴇɴᴅ ᴍᴇ ᴀ ᴛɪᴍᴇ ɪɴ ʟɪᴋᴇ ᴛʜɪs - 1h ᴏʀ 15m\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="cv_verify_time")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))
