# clone_plugins/clone_premium_menu.py
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from database import db

premium_states = {}


# ==========================================================
# 🔹 PREMIUM PLAN MENU
# ==========================================================
@Client.on_callback_query(filters.regex("^premium$"))
async def premium_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != callback_query.from_user.id:
        return await callback_query.answer("Owner only!", show_alert=True)

    text = (
        "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴇᴛᴛɪɴɢs ʜᴇʀᴇ\n\n"
        "ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ᴡᴏʀᴋ ᴏɴʟʏ ᴡʜᴇɴ ᴛᴏᴋᴇɴ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɪs ᴇɴᴀʙʟᴇᴅ"
    )

    premium_mode = await db.get_premium_mode(bot_username)
    mode_icon = "✅" if premium_mode else "❌"

    buttons = [
        [InlineKeyboardButton("Premium Plan Text", callback_data="premium_plan_text")],
        [InlineKeyboardButton("Add Premium Users", callback_data="premium_add_user"),
         InlineKeyboardButton("Remove Premium User", callback_data="premium_remove_user")],
        [InlineKeyboardButton("Premium Users List", callback_data="premium_users_list")],
        [InlineKeyboardButton(f"Premium Mode: {mode_icon}", callback_data="premium_mode_toggle")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]

    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 PREMIUM PLAN TEXT MENU
# ==========================================================
@Client.on_callback_query(filters.regex("^premium_plan_text$"))
async def premium_plan_text_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    plan_text = await db.get_premium_plan_text(bot_username)

    if plan_text:
        text = f"ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴛᴇxᴛ\n\n{plan_text}"
    else:
        text = (
            "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴛᴇxᴛ\n\n"
            "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴛᴇxᴛ"
        )

    buttons = [
        [InlineKeyboardButton("Set Premium Plan Text", callback_data="premium_set_text"),
         InlineKeyboardButton("Delete Premium Plan", callback_data="premium_delete_text")],
        [InlineKeyboardButton("🔙 Back", callback_data="premium")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^premium_set_text$"))
async def premium_set_text(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    premium_states[user_id] = "waiting_for_plan_text"

    text = (
        "ɴᴏᴡ sᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ᴘʟᴀɴ ᴛᴇxᴛ\n\n"
        "ɴᴏᴛᴇ -\n"
        "ᴘʟᴀɴ ᴛᴇxᴛ ᴍᴜsᴛ ʜᴀᴠᴇ ᴘʀɪᴄᴇ ᴅᴇᴛᴀɪʟs ᴏғ 3 ᴅᴀʏs, 1 ᴡᴇᴇᴋ ᴀɴᴅ 1 ᴍᴏɴᴛʜ ᴘʟᴀɴ "
        "ᴀɴᴅ ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴛᴀɪʟs ɪs ᴍᴜsᴛ\n\n"
        "And Send Plan Text In Minimum Words Because Of Telegram Limit\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="premium_plan_text")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=40)
async def receive_premium_plan_text(client: Client, message: Message):
    user_id = message.from_user.id
    if premium_states.get(user_id) != "waiting_for_plan_text":
        return

    premium_states.pop(user_id, None)
    plan_text = message.text
    bot_username = (await client.get_me()).username
    await db.set_premium_plan_text(bot_username, plan_text)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="premium_plan_text")]]
    await message.reply_text(
        "✅ **Premium Plan Text Saved Successfully!**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^premium_delete_text$"))
async def premium_delete_text(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_premium_plan_text(bot_username)

    await callback_query.answer("✅ Premium Plan Text Deleted.", show_alert=True)
    await premium_plan_text_menu(client, callback_query)


@Client.on_callback_query(filters.regex("^premium_add_user$"))
async def premium_add_user(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    premium_states[user_id] = "waiting_for_premium_user_id"

    text = (
        "ɴᴏᴡ sᴇɴᴅ ᴍᴇ ᴜsᴇʀ ɪᴅ\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="premium")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=41)
async def receive_add_premium_user(client: Client, message: Message):
    user_id = message.from_user.id
    if premium_states.get(user_id) != "waiting_for_premium_user_id":
        return

    try:
        target_id = int(message.text.strip())
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="premium")]]
        return await message.reply_text("❌ Invalid user ID.", reply_markup=InlineKeyboardMarkup(buttons))

    premium_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    await db.add_premium_user(target_id, bot_username)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="premium")]]
    await message.reply_text(
        f"✅ User `{target_id}` added to Premium.\n\n"
        f"Shortlinks are now disabled for this user.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^premium_remove_user$"))
async def premium_remove_user(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    premium_states[user_id] = "waiting_for_remove_premium_user"

    text = (
        "ɴᴏᴡ sᴇɴᴅ ᴍᴇ ᴜsᴇʀ ɪᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ᴘʀᴇᴍɪᴜᴍ\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="premium")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=42)
async def receive_remove_premium_user(client: Client, message: Message):
    user_id = message.from_user.id
    if premium_states.get(user_id) != "waiting_for_remove_premium_user":
        return

    try:
        target_id = int(message.text.strip())
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="premium")]]
        return await message.reply_text("❌ Invalid user ID.", reply_markup=InlineKeyboardMarkup(buttons))

    premium_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    await db.remove_premium_user(target_id, bot_username)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="premium")]]
    await message.reply_text(
        f"✅ User `{target_id}` removed from Premium.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^premium_users_list$"))
async def premium_users_list(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    users = await db.get_premium_users_list(bot_username)

    if not users:
        text = "📋 **Premium Users List**\n\nNo premium users found."
    else:
        text = "📋 **Premium Users List**\n\n"
        for i, user in enumerate(users, 1):
            text += f"{i}. `{user['user_id']}`\n"
        if len(text) > 4000:
            text = text[:4000] + "\n... (truncated)"

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="premium")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^premium_mode_toggle$"))
async def premium_mode_toggle(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    current = await db.get_premium_mode(bot_username)
    new_state = not current

    await db.set_premium_mode(bot_username, new_state)

    status = "Enabled ✅" if new_state else "Disabled ❌"
    await callback_query.answer(f"Premium Mode {status}", show_alert=True)
    await premium_menu(client, callback_query)


# ==========================================================
# 🔹 /myplan COMMAND (shows custom plan text)
# ==========================================================
@Client.on_message(filters.command("myplan") & filters.private)
async def myplan_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    plan_text = await db.get_premium_plan_text(bot_username)

    if not plan_text:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await message.reply_text(
            "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴛᴇxᴛ\n\n"
            "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ᴛᴇxᴛ",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(plan_text, reply_markup=InlineKeyboardMarkup(buttons))
