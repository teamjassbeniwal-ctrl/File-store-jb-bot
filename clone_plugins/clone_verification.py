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

# ==========================================================
# 🔹 RECEIVE INPUT
# ==========================================================
@Client.on_message(
    filters.private & filters.text & ~filters.command(
        ["cancel", "start", "help", "settings", "customize", "link", "batch", "plan", "myplan"]
    ),
    group=70
)
async def verify_receive_input(client: Client, message: Message):
    user_id = message.from_user.id
    state = vv_states.get(user_id)
    if not state:
        return

    bot_username = (await client.get_me()).username
    text = message.text.strip()

    # --- Shortlink URL ---
    if state == "waiting_verify_sl_url":
        if not (text.startswith("http://") or text.startswith("https://")):
            text = "https://" + text
        text = text.rstrip("/")
        vv_states[user_id] = {"state": "waiting_verify_sl_api", "url": text}
        return await message.reply_text("sᴇɴᴅ ᴍᴇ ᴀᴘɪ ᴋᴇʏ...")

    # --- Shortlink API ---
    if isinstance(state, dict) and state.get("state") == "waiting_verify_sl_api":
        await db.set_verify_shortlink_url(bot_username, state["url"])
        await db.set_verify_shortlink_api(bot_username, text)
        vv_states.pop(user_id, None)
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="cv_verify_sl")]]
        return await message.reply_text(
            "sᴜᴄᴄᴇssꜰᴜʟʟʏ sᴇᴛ sʜᴏʀᴛʟɪɴᴋ ✅",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # --- Tutorial ---
    if state == "waiting_verify_tt":
        await db.set_verify_tutorial(bot_username, text)
        vv_states.pop(user_id, None)
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="cv_verify_tt")]]
        return await message.reply_text(
            "✅ Tutorial link saved.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # --- Time ---
    if state == "waiting_verify_time":
        if not (text.endswith("m") or text.endswith("h")):
            return await message.reply_text("❌ Invalid format. Use 15m or 1h.")
        await db.set_verify_time(bot_username, text)
        vv_states.pop(user_id, None)
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="cv_verify_time")]]
        return await message.reply_text(
            f"✅ Time set to {text}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# ==========================================================
# 🔹 TOGGLE ON/OFF
# ==========================================================
@Client.on_callback_query(filters.regex("^cv_toggle$"))
async def verify_toggle(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    current = await db.get_verify_status(bot_username)

    if not current:
        url = await db.get_verify_shortlink_url(bot_username)
        api = await db.get_verify_shortlink_api(bot_username)
        if not url or not api:
            return await callback_query.answer(
                "⚠️ Set Verify Shortlink first.", show_alert=True
            )

    await db.set_verify_status(bot_username, not current)
    await callback_query.answer(
        f"Verification {'ON ✅' if not current else 'OFF ❌'}", show_alert=True
    )
    await token_verify_menu(client, callback_query)


# ==========================================================
# 🔹 SECOND / THIRD PLACEHOLDERS
# ==========================================================
@Client.on_callback_query(filters.regex("^cv_second$"))
async def cv_second(client: Client, callback_query: CallbackQuery):
    await callback_query.answer(
        "Second verification — duplicate the same setup with prefix 'cv2_'.",
        show_alert=True
    )


@Client.on_callback_query(filters.regex("^cv_third$"))
async def cv_third(client: Client, callback_query: CallbackQuery):
    await callback_query.answer(
        "Third verification — same pattern.",
        show_alert=True
    )
