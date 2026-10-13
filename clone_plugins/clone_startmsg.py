# clone_plugins/clone_startmsg.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db

edit_states = {}


# ==========================================================
# 🔹 START MESSAGE MENU
# ==========================================================
@Client.on_callback_query(filters.regex("^c_start_msg$"))
async def start_message_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if not clone_data or clone_data["user_id"] != callback_query.from_user.id:
        return await callback_query.answer("Owner only!", show_alert=True)

    text = (
        "📝 **START MESSAGE:**\n\n"
        "sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ: ᴡʜᴇɴ ᴜsᴇʀ ɢɪᴠᴇ sᴛᴀʀᴛ ᴄᴏᴍᴍᴀɴᴅ ᴏʀ sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴛʜᴇɴ ʙᴏᴛ ʀᴇᴘʟʏ sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ. ɪɴ sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ ʙᴏᴛ ᴏᴡɴᴇʀ ᴄᴀɴ sᴇᴛ sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ ᴛᴇxᴛ, ᴘɪᴄᴛᴜʀᴇ ᴀɴᴅ ʙᴜᴛᴛᴏɴ."
    )

    # ✅ 2 buttons per row + Back on its own row
    buttons = [
        [InlineKeyboardButton("Start Text", callback_data="c_start_text"),
         InlineKeyboardButton("Start Pic", callback_data="c_start_pic")],
        [InlineKeyboardButton("Start Button", callback_data="c_start_button")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]

    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 START TEXT MENU
# ==========================================================
@Client.on_callback_query(filters.regex("^c_start_text$"))
async def start_text_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    current_text = clone_data.get("start_text", "Default welcome message") if clone_data else "Default welcome message"

    text = (
        "📝 **START TEXT:**\n\n"
        "ᴀᴠᴀɪʟᴀʙʟᴇ ғɪʟʟɪɴɢs:\n\n"
        "{mention} - ᴜsᴇʀ - ɴᴀᴍᴇ ᴍᴇɴᴛɪᴏɴ\n"
        "{bot_mention} - ʙᴏᴛ - ɴᴀᴍᴇ ᴍᴇɴᴛɪᴏɴ\n\n"
        f"ᴛᴇxᴛ - {current_text}"
    )

    # ✅ 2 buttons per row + Back on its own row
    buttons = [
        [InlineKeyboardButton("Set Text", callback_data="c_set_start_text"),
         InlineKeyboardButton("Default Text", callback_data="c_default_start_text")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_start_msg")]
    ]

    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 SET START TEXT
# ==========================================================
@Client.on_callback_query(filters.regex("^c_set_start_text$"))
async def set_start_text(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    edit_states[user_id] = "waiting_for_start_text"

    text = (
        "sᴇɴᴅ ᴍᴇ ᴀ sᴛᴀʀᴛ ᴛᴇxᴛ.\n\n"
        "ᴀᴠᴀɪʟᴀʙʟᴇ ғɪʟʟɪɴɢs:\n\n"
        "{mention} - ᴜsᴇʀ - ɴᴀᴍᴇ ᴍᴇɴᴛɪᴏɴ\n"
        "{bot_mention} - ʙᴏᴛ - ɴᴀᴍᴇ ᴍᴇɴᴛɪᴏɴ\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_start_text")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 RECEIVE NEW START TEXT
# ==========================================================
@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=10)
async def receive_start_text(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_start_text":
        return

    edit_states.pop(user_id, None)
    new_text = message.text

    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "start_text", new_text)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_start_text")]]
    await message.reply_text("✅ Start text updated successfully!", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 DEFAULT START TEXT
# ==========================================================
@Client.on_callback_query(filters.regex("^c_default_start_text$"))
async def default_start_text(client: Client, callback_query: CallbackQuery):
    default_text = (
        "ʜᴇʏ {mention} 👋,\n\n"
        "ᴍʏ ɴᴀᴍᴇ ɪs {bot_mention}\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴀɴᴅ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss sᴛᴏʀᴇᴅ ᴍᴇssᴀɢᴇs ʙʏ ᴜsɪɴɢ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɢɪᴠᴇɴ ʙʏ ᴍᴇ.\n\n"
        "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
    )
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "start_text", default_text)
    await callback_query.answer("Default text restored!", show_alert=True)


# ==========================================================
# 🔹 START PIC
# ==========================================================
@Client.on_callback_query(filters.regex("^c_start_pic$"))
async def start_pic_menu(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    edit_states[user_id] = "waiting_for_start_pic"

    text = "🖼️ **Send me a photo** to use as the /start image.\n\n/cancel - Cancel this process."
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_start_msg")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.photo, group=11)
async def receive_start_pic(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_start_pic":
        return

    edit_states.pop(user_id, None)
    file_id = message.photo.file_id

    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "start_pic", file_id)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_start_msg")]]
    await message.reply_text("✅ Start picture updated successfully!", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 START BUTTON (Builder)
# ==========================================================
@Client.on_callback_query(filters.regex("^c_start_button$"))
async def start_button_menu(client: Client, callback_query: CallbackQuery):
    text = (
        "🔘 **START BUTTON:**\n\n"
        "ᴄʀᴇᴀᴛᴇ ᴄᴜsᴛᴏᴍ ᴜʀʟ ʙᴜᴛᴛᴏɴs ғᴏʀ ʏᴏᴜʀ sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ. ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʏᴏᴜ ᴀᴅᴅ ᴡɪʟʟ ʙᴇ sʜᴏᴡɴ ʙᴇʟᴏᴡ sᴛᴀʀᴛ ᴍᴇssᴀɢᴇ.\n\n"
        "• ᴜᴘ ᴛᴏ ᴛᴡᴏ ʙᴜᴛᴛᴏɴs ᴘᴇʀ ʀᴏᴡ\n"
        "• ᴍᴜʟᴛɪᴘʟᴇ ʀᴏᴡs sᴜᴘᴘᴏʀᴛᴇᴅ\n"
        "• ᴛʜʀᴇᴇ sᴛʏʟᴇs / ʙᴜᴛᴛᴏɴ ᴄᴏʟᴏᴜʀ ᴀᴠᴀɪʟᴀʙʟᴇ (ʀᴇᴅ, ɢʀᴇᴇɴ ᴀɴᴅ ʙʟᴜᴇ)\n\n"
        "ғᴏʟʟᴏᴡ ᴛʜᴇ ɴᴇxᴛ sᴛᴇᴘs ᴛᴏ ʙᴜɪʟᴅ ʏᴏᴜʀ ʙᴜᴛᴛᴏɴs"
    )
    buttons = [
        [InlineKeyboardButton("Add Button", callback_data="c_add_button")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_start_msg")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_add_button$"))
async def add_button_prompt(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    edit_states[user_id] = {"state": "btn_row", "row": 1, "col": 1}

    text = "📌 **ROW 1**\n\nHow many buttons do you want in this row?\n\nPlease choose an option using the keyboard below."
    # ✅ Row 1 and 2 buttons side by side, Back on new row
    buttons = [
        [InlineKeyboardButton("1", callback_data="c_row_1"),
         InlineKeyboardButton("2", callback_data="c_row_2")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_start_button")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_row_(1|2)$"))
async def row_count(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    count = int(callback_query.data.split("_")[-1])

    edit_states[user_id] = {"state": "btn_text", "row": 1, "count": count, "col": 1, "buttons": []}

    text = (
        "🔤 **BUTTON 1**\n\n"
        "Send the button text.\n\n"
        "Maximum length: 64 characters"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_add_button")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=12)
async def receive_button_text(client: Client, message: Message):
    user_id = message.from_user.id
    state = edit_states.get(user_id)
    if not isinstance(state, dict) or state.get("state") != "btn_text":
        return

    button_text = message.text[:64]
    state["buttons"].append({"text": button_text})
    state["state"] = "btn_url"

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_add_button")]]
    await message.reply_text(
        f"🔗 **Send the URL** for button '{button_text}'.\n\nExample: https://t.me/YourChannel",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=13)
async def receive_button_url(client: Client, message: Message):
    user_id = message.from_user.id
    state = edit_states.get(user_id)
    if not isinstance(state, dict) or state.get("state") != "btn_url":
        return

    url = message.text.strip()
    if not url.startswith(("http://", "https://", "tg://")):
        return await message.reply_text("❌ Invalid URL. Must start with http:// or https://")

    state["buttons"][-1]["url"] = url

    if state["col"] < state["count"]:
        state["col"] += 1
        state["state"] = "btn_text"
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_add_button")]]
        await message.reply_text(
            f"🔤 **BUTTON {state['col']}**\n\nSend the button text.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        bot_username = (await client.get_me()).username
        clone_data = await db.get_clone_by_username(bot_username)
        if clone_data:
            await db.update_clone_setting(clone_data["user_id"], "start_buttons", state["buttons"])

        edit_states.pop(user_id, None)

        # ✅ 2 buttons side by side + Back on new row
        buttons = [
            [InlineKeyboardButton("➕ Add Another Row", callback_data="c_add_button"),
             InlineKeyboardButton("✅ Done", callback_data="c_start_msg")]
        ]
        await message.reply_text(
            "✅ Row 1 saved!\n\nDo you want to add another row?",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
