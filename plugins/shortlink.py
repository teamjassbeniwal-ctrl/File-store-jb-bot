# plugins/shortlink.py
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from database import db
from config import OWNER_ID

sl_states = {}
MAIN_BOT_KEY = "MAIN_BOT"


# ==========================================================
# 🔹 SAFE EDIT HELPER
# ==========================================================
async def safe_edit(message, text, markup=None):
    try:
        await message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    except MessageNotModified:
        pass
    except Exception as e:
        print(f"Edit error: {e}")


# ==========================================================
# 🔹 SHORTLINK MENU
# ==========================================================
@Client.on_callback_query(filters.regex("^main_shortner$"))
async def main_shortlink_menu(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Owner only!", show_alert=True)

    url = await db.get_shortlink_url(MAIN_BOT_KEY)
    api = await db.get_shortlink_api(MAIN_BOT_KEY)
    status = await db.get_shortlink_status(MAIN_BOT_KEY)
    status_text = "ᴏɴ ✅" if status else "ᴏꜰꜰ ❌"

    text = (
        "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ sʜᴏʀᴛɴᴇʀ, "
        "ᴛʜᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ ʟɪɴᴋ ᴡɪʟʟ ᴄᴏɴᴠᴇʀᴛ ɪɴᴛᴏ ʏᴏᴜʀ sʜᴏʀᴛʟɪɴᴋ\n\n"
        f"sʜᴏʀᴛʟɪɴᴋ - {status_text}\n\n"
    )
    if not url:
        text += "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ sʜᴏʀᴛʟɪɴᴋ"
    else:
        text += f"🔗 URL: `{url}`\n"
        if api:
            text += f"🔑 API: `{api[:10]}...`"
        else:
            text += "🔑 API: `Not set`"

    buttons = [
        [InlineKeyboardButton("Set Shortlink", callback_data="msl_set")],
        [InlineKeyboardButton("Delete Shortlink", callback_data="msl_delete")],
        [InlineKeyboardButton("On Shortlink", callback_data="msl_on"),
         InlineKeyboardButton("Off Shortlink", callback_data="msl_off")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_back")]
    ]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 SET SHORTLINK — URL
# ==========================================================
@Client.on_callback_query(filters.regex("^msl_set$"))
async def main_shortlink_set(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Owner only!", show_alert=True)
    sl_states[callback_query.from_user.id] = "waiting_for_sl_url"
    text = (
        "sᴇɴᴅ ᴍᴇ ᴀ sʜᴏʀᴛʟɪɴᴋ ᴜʀʟ...\n\n"
        "ғᴏʀᴍᴀᴛ :\n\n"
        "https://jblink.online - ❌\n\n"
        "jblink.online - ✅\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_shortner")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 SINGLE HANDLER FOR URL + API
# ==========================================================
@Client.on_message(filters.private & filters.text & ~filters.command(["cancel", "start", "help"]), group=60)
async def receive_sl_input(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return
    user_id = message.from_user.id
    state = sl_states.get(user_id)

    # STEP 1: Waiting for URL
    if state == "waiting_for_sl_url":
        url = message.text.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
        url = url.rstrip("/")
        if "." not in url:
            return await message.reply_text("❌ Invalid URL. Try again.")

        sl_states[user_id] = {"state": "waiting_for_sl_api", "url": url}
        return await message.reply_text("sᴇɴᴅ ᴍᴇ sʜᴏʀᴛʟɪɴᴋ ᴀᴘɪ...")

    # STEP 2: Waiting for API
    if isinstance(state, dict) and state.get("state") == "waiting_for_sl_api":
        api = message.text.strip()
        url = state["url"]
        sl_states.pop(user_id, None)

        await db.set_shortlink_url(MAIN_BOT_KEY, url)
        await db.set_shortlink_api(MAIN_BOT_KEY, api)
        await db.set_shortlink_status(MAIN_BOT_KEY, True)

        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_shortner")]]
        return await message.reply_text(
            "sᴜᴄᴄᴇssꜰᴜʟʟʏ sᴇᴛ sʜᴏʀᴛʟɪɴᴋ ✅",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# ==========================================================
# 🔹 DELETE
# ==========================================================
@Client.on_callback_query(filters.regex("^msl_delete$"))
async def main_shortlink_delete(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Owner only!", show_alert=True)
    await db.delete_shortlink(MAIN_BOT_KEY)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_shortner")]]
    await safe_edit(callback_query.message, "🗑 sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ sʜᴏʀᴛʟɪɴᴋ...", InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 ON / OFF
# ==========================================================
@Client.on_callback_query(filters.regex("^msl_on$"))
async def main_shortlink_on(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Owner only!", show_alert=True)
    url = await db.get_shortlink_url(MAIN_BOT_KEY)
    api = await db.get_shortlink_api(MAIN_BOT_KEY)
    if not url or not api:
        return await callback_query.answer("⚠️ Set shortlink URL and API first.", show_alert=True)
    await db.set_shortlink_status(MAIN_BOT_KEY, True)
    await callback_query.answer("✅ Shortlink ON", show_alert=True)
    await main_shortlink_menu(client, callback_query)


@Client.on_callback_query(filters.regex("^msl_off$"))
async def main_shortlink_off(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id != OWNER_ID:
        return await callback_query.answer("Owner only!", show_alert=True)
    await db.set_shortlink_status(MAIN_BOT_KEY, False)
    await callback_query.answer("❌ Shortlink OFF", show_alert=True)
    await main_shortlink_menu(client, callback_query)
