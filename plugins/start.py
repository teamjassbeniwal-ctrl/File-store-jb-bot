# plugins/start.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from config import OWNER_ID
from utils.fsub_middleware import check_force_sub
from utils.keyboard import (
    main_settings_kb, caption_menu_kb, button_menu_kb, thumbnail_menu_kb
)
import re

edit_states = {}


# ==========================================================
# 🔹 /start
# ==========================================================
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    await db.add_user(user_id)

    bot_username = (await client.get_me()).username
    clone = await db.get_clone(user_id)

    # Force Sub gate
    is_deep_link = message.text and " " in message.text
    if not is_deep_link:
        fsub_status = await db.get_fsub_status(bot_username)
        if fsub_status:
            from utils.fsub_helper import check_subscription, build_fsub_keyboard
            not_joined = await check_subscription(client, user_id, bot_username)
            if not_joined:
                fsub_text = await db.get_fsub_text(bot_username)
                fsub_img = await db.get_fsub_image(bot_username)
                keyboard = await build_fsub_keyboard(client, bot_username, not_joined)
                msg_text = fsub_text or (
                    "📢 **Please Join Our Channels**\n\n"
                    "To use this bot, you must join the channels below.\n"
                    "After joining, click **✅ I Joined**."
                )
                if fsub_img:
                    await message.reply_photo(photo=fsub_img, caption=msg_text, reply_markup=keyboard)
                else:
                    await message.reply_text(msg_text, reply_markup=keyboard, disable_web_page_preview=True)
                return

    # Deep link handler
    if message.text and " " in message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            payload = parts[1].strip()

            if payload != "customize":
                batch_data = await db.get_batch(payload)
                if batch_data:
                    await message.reply_text(f"📦 Sending {batch_data['count']} files...")
                    for i in range(batch_data["count"]):
                        try:
                            await client.copy_message(
                                chat_id=message.chat.id,
                                from_chat_id=batch_data["from_chat_id"],
                                message_id=batch_data["start_id"] + i
                            )
                        except Exception as e:
                            print(f"Batch error: {e}")
                    return

                file_data = await db.get_stored_file(payload)
                if file_data:
                    fid = file_data["file_id"]
                    if fid.startswith("text:"):
                        await message.reply_text(fid.replace("text:", ""))
                    else:
                        await message.reply_cached_media(fid, caption="📁 **Here is your file**")
                    return

                return await message.reply_text(
                    "❌ **Invalid or Expired Link**\n\n"
                    "This link doesn't point to any stored file."
                )

    # Normal welcome message
    text = (
        f"ʜᴇʏ {first_name} 👋,\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴡɪᴛʜ ᴄʟᴏɴᴇ ᴀɴᴅ ᴍᴀɴʏ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇ ᴀɴᴅ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss sᴛᴏʀᴇᴅ ᴍᴇssᴀɢᴇs ʙʏ ᴜsɪɴɢ ᴀ sʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ ɢɪᴠᴇɴ ʙʏ ᴍᴇ\n\n"
        "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
    )

    buttons = [
        [InlineKeyboardButton("Help", callback_data="main_help"),
         InlineKeyboardButton("About", callback_data="main_about")],
        [InlineKeyboardButton("Create Own Clone", callback_data="create_clone")],
        [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
         InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
    ]

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 /help
# ==========================================================
@Client.on_message(filters.command("help") & filters.private)
async def help_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return
    await send_help_menu(message)


@Client.on_callback_query(filters.regex("^main_help$"))
async def help_callback(client: Client, callback_query: CallbackQuery):
    await send_help_menu(callback_query.message, edit=True)


async def send_help_menu(message, edit=False):
    help_text = (
        "🎓 **HELP MENU:**\n\n"
        "🤖 ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ\n"
        "🔗 ᴀꜰᴛᴇʀ ꜱᴛᴏʀɪɴɢ, ɪ ᴡɪʟʟ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ꜱʜᴀʀᴇᴀʙʟᴇ ʟɪɴᴋ.\n\n"
        "📚 **BASIC COMMANDS**\n"
        "➤ /start - ᴄʜᴇᴄᴋ ɪꜰ ɪ'ᴍ ᴀʟɪᴠᴇ.\n"
        "➤ /id - ɢᴇᴛ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ.\n\n"
        "📦 **FILE STORAGE COMMANDS**\n"
        "➤ /link - ꜱᴛᴏʀᴇ ᴀ ꜱɪɴɢʟᴇ ꜰɪʟᴇ.\n"
        "➤ /batch - ꜱᴛᴏʀᴇ ᴍᴜʟᴛɪᴘʟᴇ ꜰɪʟᴇꜱ.\n\n"
        "💎 **PREMIUM COMMANDS**\n"
        "➤ /myplan - ᴠɪᴇᴡ ʏᴏᴜʀ ᴘʟᴀɴ.\n\n"
        "🤖 **CLONE BOT COMMANDS**\n"
        "➤ /clone - ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ.\n"
        "➤ /activate - ᴀᴄᴛɪᴠᴀᴛᴇ ᴄʟᴏɴᴇ.\n"
        "➤ /delete - ᴅᴇʟᴇᴛᴇ ᴄʟᴏɴᴇ.\n\n"
        "⚙️ **USER SETTINGS**\n"
        "➤ /settings - ᴄᴜꜱᴛᴏᴍɪᴢᴇ ꜱᴇᴛᴛɪɴɢꜱ.\n\n"
        "👑 **ADMIN COMMANDS**\n"
        "➤ /broadcast - ʙʀᴏᴀᴅᴄᴀꜱᴛ (ᴏᴡɴᴇʀ ᴏɴʟʏ)."
    )
    buttons = [
        [InlineKeyboardButton("Settings", callback_data="main_settings"),
         InlineKeyboardButton("About", callback_data="main_about")],
        [InlineKeyboardButton("Back", callback_data="main_back")]
    ]
    if edit:
        await message.edit_text(help_text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(help_text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 /about
# ==========================================================
@Client.on_message(filters.command("about") & filters.private)
async def about_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return
    await send_about_menu(message)


@Client.on_callback_query(filters.regex("^main_about$"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    await send_about_menu(callback_query.message, edit=True)


async def send_about_menu(message, edit=False):
    about_text = (
        "○ **Creator** : King VJ\n"
        "○ **Language** : Python3\n"
        "○ **Library** : Pyrogram 2.0.106\n"
        "○ **Channel** : @teamjb1\n"
        "○ **Support Group** : @jbsupportgroup"
    )
    buttons = [
        [InlineKeyboardButton("Settings", callback_data="main_settings"),
         InlineKeyboardButton("Help", callback_data="main_help")],
        [InlineKeyboardButton("Back", callback_data="main_back")]
    ]
    if edit:
        await message.edit_text(about_text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(about_text, reply_markup=InlineKeyboardMarkup(buttons))

# ==========================================================
# 🔹 /id
# ==========================================================
@Client.on_message(filters.command("id") & filters.private)
async def id_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return

    user = message.from_user
    text = (
        "User Details :\n\n\n"
        f"🦚 **First Name** : {user.first_name}\n\n"
        f"🐧 **Last Name** : {user.last_name or 'None'}\n\n"
        f"👤 **User Id** : `{user.id}`\n\n"
        f"👦 **Username** : @{user.username or 'None'}\n\n"
        f"🔗 **User Link** : {user.mention}\n\n"
        f"🌟 **Telegram Premium** : {'True' if user.is_premium else 'False'}\n\n"
        f"📃 **Language Code** : {user.language_code}\n\n"
        "💫 **Status** : Recently"
    )
    await message.reply_text(text)


# ==========================================================
# 🔹 /settings
# ==========================================================
@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return
    await send_main_settings(message)


@Client.on_callback_query(filters.regex("^main_settings$"))
async def settings_callback(client: Client, callback_query: CallbackQuery):
    await send_main_settings(callback_query.message, edit=True)


async def send_main_settings(message, edit=False):
    text = (
        "⚙️ **SETTINGS:**\n\n"
        "ᴄᴜsᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴀs ᴘᴇʀ ʏᴏᴜʀ ɴᴇᴇᴅ.\n\n"
        "ɴᴏᴛᴇ: ᴛʜᴇ sᴇᴛᴛɪɴɢs ʙᴇʟᴏᴡ ᴡɪʟʟ ᴏɴʟʏ ᴡᴏʀᴋ ғᴏʀ ʟɪɴᴋs ᴄʀᴇᴀᴛᴇᴅ ʙʏ ᴛʜɪs ᴀᴄᴄᴏᴜɴᴛ."
    )
    if edit:
        await message.edit_text(text, reply_markup=main_settings_kb())
    else:
        await message.reply_text(text, reply_markup=main_settings_kb())


# ==========================================================
# 🔹 MAIN BOT — CAPTION
# ==========================================================
@Client.on_callback_query(filters.regex("^main_caption$"))
async def main_caption_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    caption = await db.get_custom_caption(bot_username)

    text = (
        "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ɢɪᴠᴇɴ ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ.\n\n"
        f"ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ - {caption or '{file_name}'}"
    )
    await callback_query.message.edit_text(text, reply_markup=caption_menu_kb())


@Client.on_callback_query(filters.regex("^main_set_caption$"))
async def main_set_caption_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "main_waiting_for_caption"
    text = (
        "sᴇɴᴅ ᴍᴇ ᴀ ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ.\n\n"
        "ᴀᴠᴀɪʟᴀʙʟᴇ ғɪʟʟɪɴɢ:-\n{file_name}\n{file_size}\n{originalcaption}\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_caption")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^main_default_caption$"))
async def main_default_caption(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_custom_caption(bot_username)
    await callback_query.answer("✅ Default caption set.", show_alert=True)
    await main_caption_menu(client, callback_query)


# ==========================================================
# 🔹 MAIN BOT — BUTTONS
# ==========================================================
@Client.on_callback_query(filters.regex("^main_button$"))
async def main_button_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    buttons_data = await db.get_custom_buttons(bot_username)

    text = (
        "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ sᴇᴛ ᴀ ʙᴜᴛᴛᴏɴ ꜰᴏʀ ʏᴏᴜʀ ꜰɪʟᴇ.\n\n"
        "ғᴏʀᴍᴀᴛ:\n"
        "[vj bot][buttonurl:https://t.me/vj_botz]"
    )
    await callback_query.message.edit_text(
        text, reply_markup=button_menu_kb(bool(buttons_data))
    )


@Client.on_callback_query(filters.regex("^main_add_buttons$"))
async def main_add_buttons_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "main_waiting_for_buttons"
    text = (
        "sᴇɴᴅ ᴍᴇ ᴀ ʙᴜᴛᴛᴏɴ ɪɴ ᴛʜɪs ꜰᴏʀᴍᴀᴛ:\n\n"
        "[Button Text][buttonurl:https://link.com]\n\n"
        "/cancel - Cancel"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_button")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^main_see_buttons$"))
async def main_see_buttons(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    buttons_data = await db.get_custom_buttons(bot_username)

    text = "📋 **Current Buttons:**\n\n"
    for row in buttons_data:
        for btn in row:
            text += f"• `{btn['text']}` → {btn['url']}\n"
        text += "\n"

    back_buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_button")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(back_buttons))


@Client.on_callback_query(filters.regex("^main_remove_buttons$"))
async def main_remove_buttons(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_custom_buttons(bot_username)
    await callback_query.answer("✅ Buttons removed.", show_alert=True)
    await main_button_menu(client, callback_query)


# ==========================================================
# 🔹 MAIN BOT — THUMBNAIL
# ==========================================================
@Client.on_callback_query(filters.regex("^main_thumbnail$"))
async def main_thumbnail_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    thumb = await db.get_custom_thumbnail(bot_username)

    text = (
        "🖼️ **CUSTOM THUMBNAIL:**\n\n"
        "ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ: ɪᴛ ɪs ᴀ ᴄᴏᴠᴇʀ ᴛʜᴜᴍʙɴᴀɪʟ ғᴏʀ ᴠɪᴅᴇᴏ ғɪʟᴇ.\n\n"
    )
    text += "✅ Thumbnail added." if thumb else "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ᴘɪᴄᴛᴜʀᴇ..."
    await callback_query.message.edit_text(text, reply_markup=thumbnail_menu_kb())


@Client.on_callback_query(filters.regex("^main_set_thumb$"))
async def main_set_thumb_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "main_waiting_for_thumb"
    text = "sᴇɴᴅ ᴍᴇ ᴀ ᴘɪᴄᴛᴜʀᴇ.\n\n/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss."
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_thumbnail")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^main_view_thumb$"))
async def main_view_thumb(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    thumb = await db.get_custom_thumbnail(bot_username)

    if not thumb:
        return await callback_query.answer("⚠️ No thumbnail set.", show_alert=True)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_thumbnail")]]
    await client.send_photo(
        callback_query.message.chat.id,
        photo=thumb,
        caption="🖼️ **Current Thumbnail**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^main_remove_thumb$"))
async def main_remove_thumb(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_custom_thumbnail(bot_username)
    await callback_query.answer("✅ Thumbnail removed.", show_alert=True)
    await main_thumbnail_menu(client, callback_query)


# ==========================================================
# 🔹 MAIN BOT — AUTO DELETE (NOT AVAILABLE)
# ==========================================================
@Client.on_callback_query(filters.regex("^main_auto_delete$"))
async def main_auto_delete(client: Client, callback_query: CallbackQuery):
    await callback_query.answer(
        "⚠️ Auto delete feature is not available in this bot due to copyright issues.\n\n"
        "It's available in clone bots only.",
        show_alert=True
    )

# ==========================================================
# 🔹 MAIN BOT — RECEIVE CAPTION
# ==========================================================
@Client.on_message(
    filters.private & filters.text & ~filters.command(["cancel", "start"]),
    group=85
)
async def main_receive_caption(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "main_waiting_for_caption":
        return

    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    await db.set_custom_caption(bot_username, message.text)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_caption")]]
    await message.reply_text("✅ Caption saved.", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 MAIN BOT — RECEIVE BUTTONS
# ==========================================================
@Client.on_message(
    filters.private & filters.text & ~filters.command(["cancel", "start"]),
    group=86
)
async def main_receive_buttons(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "main_waiting_for_buttons":
        return

    edit_states.pop(user_id, None)
    text = message.text.strip()

    pattern = r"\[([^\]]+)\]\[buttonurl:([^\]]+)\]"
    matches = re.findall(pattern, text)

    if not matches:
        return await message.reply_text(
            "❌ Invalid format. Use: [Button Text][buttonurl:https://link.com]"
        )

    parsed_rows = []
    current_row = []
    for btn_text, url in matches:
        current_row.append({"text": btn_text, "url": url})
        if len(current_row) == 2:
            parsed_rows.append(current_row)
            current_row = []
    if current_row:
        parsed_rows.append(current_row)

    bot_username = (await client.get_me()).username
    await db.set_custom_buttons(bot_username, parsed_rows)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_button")]]
    await message.reply_text("✅ Buttons saved.", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 MAIN BOT — RECEIVE THUMBNAIL
# ==========================================================
@Client.on_message(filters.private & filters.photo, group=88)
async def main_receive_thumb(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "main_waiting_for_thumb":
        return

    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    await db.set_custom_thumbnail(bot_username, message.photo.file_id)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_thumbnail")]]
    await message.reply_text("✅ Thumbnail saved.", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 BACK
# ==========================================================
@Client.on_callback_query(filters.regex("^main_back$"))
async def back_callback(client: Client, callback_query: CallbackQuery):
    first_name = callback_query.from_user.first_name
    text = (
        f"ʜᴇʏ {first_name} 👋,\n\n"
        "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ ᴡɪᴛʜ ᴄʟᴏɴᴇ ᴀɴᴅ ᴍᴀɴʏ ᴀᴍᴀᴢɪɴɢ ᴀᴅᴠᴀɴᴄᴇ ғᴇᴀᴛᴜʀᴇ.\n\n"
        "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
    )
    buttons = [
        [InlineKeyboardButton("Help", callback_data="main_help"),
         InlineKeyboardButton("About", callback_data="main_about")],
        [InlineKeyboardButton("Create Own Clone", callback_data="create_clone")],
        [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
         InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 CANCEL
# ==========================================================
@Client.on_message(filters.command("cancel") & filters.private, group=89)
async def main_cancel(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in edit_states:
        edit_states.pop(user_id, None)
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_settings")]]
        await message.reply_text("✅ Cancelled.", reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 OTHER SETTINGS ALERTS
# ==========================================================
@Client.on_callback_query(
    filters.regex("^main_(free_limit|refer|permanent_link|protect_content)$")
)
async def main_setting_alert(client: Client, callback_query: CallbackQuery):
    key = callback_query.data.replace("main_", "")
    messages = {
        "free_limit": "🆓 Free usage: 5 files per day.",
        "refer": "🌍 Refer & Earn: Coming soon!",
        "permanent_link": "♾️ Permanent Link: Toggle.",
        "protect_content": "🔒 Protect Content: Toggle."
    }
    await callback_query.answer(messages.get(key, "Coming soon"), show_alert=True)


# ==========================================================
# 🔹 /broadcast
# ==========================================================
@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_cmd(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("❌ Owner only command.")

    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a message to broadcast.")

    users = await db.get_all_users()
    status = await message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    success = 0
    for u in users:
        try:
            await message.reply_to_message.copy(u["user_id"])
            success += 1
        except Exception:
            pass
    await status.edit_text(f"✅ Sent to {success}/{len(users)} users.")
