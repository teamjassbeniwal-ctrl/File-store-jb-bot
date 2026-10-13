# clone_plugins/clone_shortlink.py
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db

sl_states = {}


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
            text += f"🔑 API: `{api[:8]}...`"

    buttons = [
        [InlineKeyboardButton("Set Shortlink", callback_data="sl_set")],
        [InlineKeyboardButton("Delete Shortlink", callback_data="sl_delete")],
        [InlineKeyboardButton("On Shortlink", callback_data="sl_on"),
         InlineKeyboardButton("Off Shortlink", callback_data="sl_off")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


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
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=50)
async def receive_sl_url(client: Client, message: Message):
    user_id = message.from_user.id
    if sl_states.get(user_id) != "waiting_for_sl_url":
        return

    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    url = url.rstrip("/")
    sl_states[user_id] = {"state": "waiting_for_sl_api", "url": url}
    await message.reply_text("sᴇɴᴅ ᴍᴇ sʜᴏʀᴛʟɪɴᴋ ᴀᴘɪ...")


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=51)
async def receive_sl_api(client: Client, message: Message):
    user_id = message.from_user.id
    state = sl_states.get(user_id)
    if not isinstance(state, dict) or state.get("state") != "waiting_for_sl_api":
        return
    api = message.text.strip()
    url = state["url"]
    sl_states.pop(user_id, None)

    bot_username = (await client.get_me()).username
    await db.set_shortlink_url(bot_username, url)
    await db.set_shortlink_api(bot_username, api)
    await db.set_shortlink_status(bot_username, True)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_shortner")]]
    await message.reply_text(
        "sᴜᴄᴄᴇssꜰᴜʟʟʏ sᴇᴛ sʜᴏʀᴛʟɪɴᴋ ✅",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^sl_delete$"))
async def shortlink_delete(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_shortlink(bot_username)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_shortner")]]
    await callback_query.message.edit_text(
        "🗑 sᴜᴄᴄᴇssꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ sʜᴏʀᴛʟɪɴᴋ...",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^sl_on$"))
async def shortlink_on(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    url = await db.get_shortlink_url(bot_username)
    if not url:
        return await callback_query.answer("⚠️ Set shortlink first.", show_alert=True)
    await db.set_shortlink_status(bot_username, True)
    await callback_query.answer("✅ Shortlink ON", show_alert=True)
    await shortlink_menu(client, callback_query)


@Client.on_callback_query(filters.regex("^sl_off$"))
async def shortlink_off(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.set_shortlink_status(bot_username, False)
    await callback_query.answer("❌ Shortlink OFF", show_alert=True)
    await shortlink_menu(client, callback_query)
