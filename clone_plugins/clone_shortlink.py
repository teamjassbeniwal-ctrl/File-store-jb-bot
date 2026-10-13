# clone_plugins/clone_shortlink.py
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from database import db

sl_states = {}


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
@Client.on_callback_query(filters.regex("^u_shortner$"))
async def shortlink_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    url = await db.get_shortlink_url(bot_username)
    api = await db.get_shortlink_api(bot_username)
    status = await db.get_shortlink_status(bot_username)
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
        [InlineKeyboardButton("Set Shortlink", callback_data="sl_set")],
        [InlineKeyboardButton("Delete Shortlink", callback_data="sl_delete")],
        [InlineKeyboardButton("On Shortlink", callback_data="sl_on"),
         InlineKeyboardButton("Off Shortlink", callback_data="sl_off")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 SET SHORTLINK
# ==========================================================
@Client.on_callback_query(filters.regex("^sl_set$"))
async def shortlink_set(client: Client, callback_query: CallbackQuery):
    sl_states[callback_query.from_user.id] = "waiting_for_sl_url"
    text = (
        "sᴇɴᴅ ᴍᴇ ᴀ sʜᴏʀᴛʟɪɴᴋ ᴜʀʟ...\n\n"
        "ғᴏʀᴍᴀᴛ :\n\n"
        "https://jblink.online - ❌\n\n"
        "jblink.online - ✅\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_shortner")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 SINGLE HANDLER FOR URL + API
# ==========================================================
@Client.on_message(filters.private & filters.text & ~filters.command(["cancel", "start", "help"]), group=50)
async def receive_sl_input(client: Client, message: Message):
    user_id = message.from_user.id
    state = sl_states.get(user_id)

    if state == "waiting_for_sl_url":
        url = message.text.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "https://" + url
        url = url.rstrip("/")
        if "." not in url:
            return await message.reply_text("❌ Invalid URL. Try again.")

        sl_states[user_id] = {"state": "waiting_for_sl_api", "url": url}
        return await message.reply_text("sᴇɴᴅ ᴍᴇ sʜᴏʀᴛʟɪɴᴋ ᴀᴘɪ...")

    if isinstance(state, dict) and state.get("state") == "waiting_for_sl_api":
        api = message.text.strip()
        url = state["url"]
        sl_states.pop(user_id, None)

        bot_username = (await client.get_me()).username
        await db.set_shortlink_url(bot_username, url)
        await db.set_shortlink_api(bot_username, api)
        await db.set_shortlink_status(bot_username, True)

        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_shortner")]]
        return await message.reply_text(
            "sᴜᴄᴄᴇssꜰᴜʟʟʏ sᴇᴛ sʜᴏʀᴛʟɪɴᴋ ✅",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# ==========================================================
# 🔹 DELETE
# ==========================================================
@Client.on_callback_query(filters.regex("^sl_delete$"))
async def shortlink_delete(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_shortlink(bot_username)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_shortner")]]
    await safe_edit(callback_query.message, "🗑 sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ sʜᴏʀᴛʟɪɴᴋ...", InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 ON / OFF
# ==========================================================
@Client.on_callback_query(filters.regex("^sl_on$"))
async def shortlink_on(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    url = await db.get_shortlink_url(bot_username)
    api = await db.get_shortlink_api(bot_username)
    if not url or not api:
        return await callback_query.answer("⚠️ Set shortlink URL and API first.", show_alert=True)
    await db.set_shortlink_status(bot_username, True)
    await callback_query.answer("✅ Shortlink ON", show_alert=True)
    await shortlink_menu(client, callback_query)


@Client.on_callback_query(filters.regex("^sl_off$"))
async def shortlink_off(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.set_shortlink_status(bot_username, False)
    await callback_query.answer("❌ Shortlink OFF", show_alert=True)
    await shortlink_menu(client, callback_query)
