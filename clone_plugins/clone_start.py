# clone_plugins/clone_start.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from utils.fsub_middleware import check_force_sub
import asyncio
import psutil
import time
import re

edit_states = {}
BOT_START_TIME = time.time()


# ==========================================================
# 🔹 AUTO DELETE HELPER (For Deep Links)
# ==========================================================
async def _auto_delete_file(client: Client, message, seconds: int, user_id: int, unique_id: str):
    print(f"⏱️ Auto-delete: waiting {seconds}s")
    
    # 1. Send the "IMPORTANT" warning message
    try:
        warning_text = (
            "‼️ ‼️ ‼️ **IMPORTANT** ‼️ ‼️ ‼️\n\n"
            f"**THIS MESSAGE WILL BE DELETED IN {seconds // 60} Minutes** 🙁 **(DUE TO COPYRIGHT ISSUES).**\n\n"
            "**PLEASE FORWARD THIS MESSAGE TO YOUR SAVED MESSAGES OR ANY PRIVATE CHAT TO AVOID LOSING.**"
        )
        await message.reply_text(warning_text)
    except Exception as e:
        print(f"Warning send failed: {e}")

    # 2. Wait for the specified time
    await asyncio.sleep(seconds)

    try:
        # 3. Delete the original file message
        await message.delete()
        print("✅ File deleted.")
        
        # 4. Send the "PREVIOUS MESSAGE IS DELETED" recovery menu
        recovery_text = (
            "🍿 **PREVIOUS MESSAGE IS DELETED**\n\n"
            "**IF YOU WANT THIS PREVIOUS MESSAGE AGAIN THEN CLICK ON BELOW BUTTON OTHERWISE CLICK ON CLOSE BUTTON.**"
        )
        buttons = [
            [InlineKeyboardButton("✅ GET MESSAGE AGAIN ✅", callback_data=f"get_again_{unique_id}")],
            [InlineKeyboardButton("🔪 CLOSE 🔪", callback_data="close_recovery")]
        ]
        
        await client.send_message(
            chat_id=user_id,
            text=recovery_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        print("✅ Recovery menu sent.")
        
    except Exception as e:
        print(f"⚠️ Auto-delete process failed: {type(e).__name__}: {e}")


# ==========================================================
# 🔹 /start
# ==========================================================
@Client.on_message(filters.command("start") & filters.private)
async def clone_start(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    bot_mention = f"@{bot_username}"
    user_mention = message.from_user.mention

    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data and clone_data.get("log_channel"):
        try:
            await client.send_message(
                clone_data["log_channel"],
                f"🆕 **New User Started**\n\n"
                f"👤 {message.from_user.first_name}\n"
                f"🆔 `{user_id}`\n"
                f"📛 @{message.from_user.username or 'None'}"
            )
        except Exception as e:
            print(f"Log channel error: {e}")

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
                msg_text = fsub_text or "📢 **Please Join Our Channels**\n\nAfter joining, click **✅ I Joined**."
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

            if payload == "customize":
                if clone_data and clone_data["user_id"] == user_id:
                    await send_clone_settings(message)
                    return
                else:
                    return await message.reply_text("⚠️ Only the bot owner can customize this bot.")

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

            stored = await db.get_stored_file(payload)
            if stored:
                if stored["type"] == "single":
                    fid = stored["file_id"]
                    if fid.startswith("text:"):
                        await message.reply_text(fid.replace("text:", ""))
                    else:
                        caption = await db.get_custom_caption(bot_username)
                        buttons_data = await db.get_custom_buttons(bot_username)
                        thumb = await db.get_custom_thumbnail(bot_username)
                        autodel_status = await db.get_auto_delete_status(bot_username)
                        autodel_time = await db.get_auto_delete_time(bot_username)

                        # Build caption
                        if not caption:
                            caption = "🧐 **HERE IS YOUR LINK :**\n\n🖇️ `{final_link}`"
                        
                        final_link = f"https://telegram.me/{bot_username}?start={payload}"
                        caption = caption.replace("{final_link}", final_link)

                        # Build keyboard
                        keyboard = []
                        for row in buttons_data:
                            kb_row = []
                            for btn in row:
                                kb_row.append(InlineKeyboardButton(btn["text"], url=btn["url"]))
                            keyboard.append(kb_row)

                        keyboard.append([InlineKeyboardButton("📋 Copy Link 🔗", callback_data=f"copy_link_{payload}")])
                        keyboard.append([InlineKeyboardButton("♻️ SHARE URL ♻️", url=f"https://t.me/share/url?url={final_link}")])

                        reply_markup = InlineKeyboardMarkup(keyboard)

                        try:
                            sent = await client.send_cached_media(
                                chat_id=message.chat.id,
                                file_id=fid,
                                caption=caption,
                                thumb=thumb,
                                reply_markup=reply_markup
                            )
                            if autodel_status and sent:
                                try:
                                    time_str = autodel_time.strip().lower()
                                    if time_str.endswith("m"):
                                        seconds = int(time_str[:-1]) * 60
                                    elif time_str.endswith("h"):
                                        seconds = int(time_str[:-1]) * 3600
                                    elif time_str.endswith("s"):
                                        seconds = int(time_str[:-1])
                                    else:
                                        seconds = 60
                                    print(f"⏱️ Scheduling auto-delete in {seconds}s (deep link)")
                                    asyncio.create_task(_auto_delete_file(client, sent, seconds, user_id, payload))
                                except Exception as e:
                                    print(f"⚠️ Auto-delete error: {e}")
                        except Exception as e:
                            print(f"File delivery error: {type(e).__name__}: {e}")
                            await message.reply_cached_media(fid, caption=caption)
                return

            return await message.reply_text(
                "❌ **Invalid or Expired Link**\n\n"
                "This link doesn't point to any stored file."
            )

    # Normal /start
    start_text = clone_data.get("start_text") if clone_data else None
    start_pic = clone_data.get("start_pic") if clone_data else None
    start_buttons = clone_data.get("start_buttons", []) if clone_data else []

    if not start_text:
        start_text = (
            "ʜᴇʏ {mention} 👋,\n\n"
            "ᴍʏ ɴᴀᴍᴇ ɪs {bot_mention}\n\n"
            "ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ.\n\n"
            "ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴄʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ."
        )

    try:
        formatted_text = start_text.format(mention=user_mention, bot_mention=bot_mention)
    except Exception:
        formatted_text = start_text

    keyboard = []
    for btn in start_buttons:
        keyboard.append([InlineKeyboardButton(btn["text"], url=btn["url"])])

    if not keyboard:
        keyboard = [
            [InlineKeyboardButton("Help", callback_data="c_help"),
             InlineKeyboardButton("About", callback_data="c_about")],
            [InlineKeyboardButton("Settings", callback_data="c_settings"),
             InlineKeyboardButton("Customize", url=f"https://t.me/{bot_username}?start=customize")],
            [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
             InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if start_pic:
        await message.reply_photo(photo=start_pic, caption=formatted_text, reply_markup=reply_markup)
    else:
        await message.reply_text(formatted_text, reply_markup=reply_markup)


# ==========================================================
# 🔹 CALLBACK HANDLERS FOR RECOVERY MENU & COPY LINK
# ==========================================================

@Client.on_callback_query(filters.regex("^copy_link_"))
async def copy_link_cb(client: Client, callback_query: CallbackQuery):
    unique_id = callback_query.data.replace("copy_link_", "")
    bot_username = (await client.get_me()).username
    final_link = f"https://telegram.me/{bot_username}?start={unique_id}"
    
    await callback_query.answer("Link copied to clipboard!", show_alert=False)
    # Send a temporary message that the user can easily copy
    await callback_query.message.reply_text(
        f"`{final_link}`",
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex("^get_again_"))
async def get_again_cb(client: Client, callback_query: CallbackQuery):
    unique_id = callback_query.data.replace("get_again_", "")
    bot_username = (await client.get_me()).username
    
    # 1. Acknowledge
    await callback_query.answer("Fetching message...", show_alert=False)
    
    # 2. Delete the recovery menu message
    try:
        await callback_query.message.delete()
    except Exception:
        pass

    # 3. Resend the file (logic similar to /start deep link)
    stored = await db.get_stored_file(unique_id)
    if not stored:
        return await client.send_message(callback_query.from_user.id, "❌ File not found. It may have been deleted.")

    fid = stored["file_id"]
    if fid.startswith("text:"):
        return await client.send_message(callback_query.from_user.id, fid.replace("text:", ""))

    caption = await db.get_custom_caption(bot_username)
    buttons_data = await db.get_custom_buttons(bot_username)
    thumb = await db.get_custom_thumbnail(bot_username)
    autodel_status = await db.get_auto_delete_status(bot_username)
    autodel_time = await db.get_auto_delete_time(bot_username)

    final_link = f"https://telegram.me/{bot_username}?start={unique_id}"
    if not caption:
        caption = "🧐 **HERE IS YOUR LINK :**\n\n🖇️ `{final_link}`"
    caption = caption.replace("{final_link}", final_link)

    keyboard = []
    for row in buttons_data:
        kb_row = []
        for btn in row:
            kb_row.append(InlineKeyboardButton(btn["text"], url=btn["url"]))
        keyboard.append(kb_row)
    
    keyboard.append([InlineKeyboardButton("📋 Copy Link 🔗", callback_data=f"copy_link_{unique_id}")])
    keyboard.append([InlineKeyboardButton("♻️ SHARE URL ♻️", url=f"https://t.me/share/url?url={final_link}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        sent = await client.send_cached_media(
            chat_id=callback_query.from_user.id,
            file_id=fid,
            caption=caption,
            thumb=thumb,
            reply_markup=reply_markup
        )
        # Re-schedule auto delete
        if autodel_status and sent:
            time_str = autodel_time.strip().lower()
            if time_str.endswith("m"):
                seconds = int(time_str[:-1]) * 60
            elif time_str.endswith("h"):
                seconds = int(time_str[:-1]) * 3600
            elif time_str.endswith("s"):
                seconds = int(time_str[:-1])
            else:
                seconds = 60
            asyncio.create_task(_auto_delete_file(client, sent, seconds, callback_query.from_user.id, unique_id))
    except Exception as e:
        print(f"Error resending file: {e}")
        await client.send_message(callback_query.from_user.id, "❌ Failed to fetch the file. It might have been deleted from Telegram servers.")

@Client.on_callback_query(filters.regex("^close_recovery$"))
async def close_recovery_cb(client: Client, callback_query: CallbackQuery):
    try:
        await callback_query.message.delete()
    except Exception:
        pass
    await callback_query.answer("Closed", show_alert=False)


# ==========================================================
# 🔹 HELP, ABOUT, ID, SETTINGS (Unchanged)
# ==========================================================
@Client.on_message(filters.command("help") & filters.private)
async def clone_help_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return
    await send_clone_help(message)


@Client.on_callback_query(filters.regex("^c_help$"))
async def clone_help_cb(client: Client, callback_query: CallbackQuery):
    await send_clone_help(callback_query.message, edit=True)


async def send_clone_help(message, edit=False):
    text = (
        "🎓 **HELP MENU:**\n\n"
        "🤖 ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ\n\n"
        "📚 **BASIC**\n➤ /start\n➤ /id\n\n"
        "📦 **FILE STORAGE**\n➤ /link\n➤ /batch\n\n"
        "💎 **PREMIUM**\n➤ /myplan\n➤ /redeem\n\n"
        "⚙️ **SETTINGS**\n➤ /settings\n\n"
        "👑 **ADMIN**\n➤ /customize\n➤ /broadcast\n➤ /ban\n➤ /unban"
    )
    buttons = [
        [InlineKeyboardButton("Settings", callback_data="c_settings"),
         InlineKeyboardButton("About", callback_data="c_about")],
        [InlineKeyboardButton("Back", callback_data="c_back")]
    ]
    if edit:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_about$"))
async def clone_about_cb(client: Client, callback_query: CallbackQuery):
    text = (
        "○ **Creator** : King VJ\n"
        "○ **Language** : Python3\n"
        "○ **Library** : Pyrogram 2.0.106\n"
        "○ **Channel** : @teamjb1\n"
        "○ **Support Group** : @jbsupportgroup"
    )
    buttons = [
        [InlineKeyboardButton("Settings", callback_data="c_settings"),
         InlineKeyboardButton("Help", callback_data="c_help")],
        [InlineKeyboardButton("Back", callback_data="c_back")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command("id") & filters.private)
async def clone_id_cmd(client: Client, message: Message):
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


@Client.on_message(filters.command("settings") & filters.private)
async def user_settings_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return
    await send_user_settings(message)


@Client.on_callback_query(filters.regex("^c_settings$"))
async def user_settings_cb(client: Client, callback_query: CallbackQuery):
    await send_user_settings(callback_query.message, edit=True)


async def send_user_settings(message, edit=False):
    text = "⚙️ **SETTINGS:**\n\nᴄᴜsᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs ᴀs ᴘᴇʀ ʏᴏᴜʀ ɴᴇᴇᴅ."
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
    if edit:
        await message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.command("customize") & filters.private)
async def customize_cmd(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return
    clone_data = await db.get_clone_by_username(bot_username)
    if not clone_data or clone_data["user_id"] != message.from_user.id:
        return await message.reply_text("⚠️ Only the bot owner can use this command.")
    await send_clone_settings(message)


async def send_clone_settings(message, edit=False):
    text = (
        "🛠️ **CLONE MENU**\n\n"
        "WELCOME TO YOUR CLONE BOT MANAGEMENT HUB!\n\n"
        "⚙️ **QUICK COMMANDS**\n"
        "🚀 /activate\n🗑️ /delete"
    )
    buttons = [
        [InlineKeyboardButton("💰 MONETIZATION", callback_data="c_monetization"),
         InlineKeyboardButton("💎 PREMIUM PLAN", callback_data="premium")],
        [InlineKeyboardButton("📝 START MESSAGE", callback_data="c_start_msg"),
  

@Client.on_callback_query(filters.regex("^c_log_channel$"))
async def log_channel_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    log_channel = clone_data.get("log_channel") if clone_data else None
    text = "📢 **LOG CHANNEL:**\n\n"
    text += f"✅ **Current:** `{log_channel}`" if log_channel else "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ❗️"
    buttons = [
        [InlineKeyboardButton("Set Log Channel", callback_data="c_set_log")],
        [InlineKeyboardButton("Delete Channel", callback_data="c_delete_log")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_set_log$"))
async def set_log_channel(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_log_channel"
    bot_username = (await client.get_me()).username
    text = f"ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ʏᴏᴜʀ ʟᴏɢ ᴄʜᴀɴɴᴇʟ.\nᴍᴀᴋᴇ sᴜʀᴇ @{bot_username} ɪs ᴀᴅᴍɪɴ.\n\n/cancel"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_delete_log$"))
async def delete_log_channel(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "log_channel", None)
    await callback_query.answer("✅ Deleted.", show_alert=True)
    await log_channel_menu(client, callback_query)


@Client.on_callback_query(filters.regex("^c_db_channel$"))
async def db_channel_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    db_channel = clone_data.get("db_channel") if clone_data else None
    text = "☁️ **DATABASE CHANNEL:**\n\n"
    text += f"✅ **Current:** `{db_channel}`" if db_channel else "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ❗️"
    buttons = [
        [InlineKeyboardButton("Set Database Channel", callback_data="c_set_db")],
        [InlineKeyboardButton("Delete Channel", callback_data="c_delete_db")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_set_db$"))
async def set_db_channel(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_db_channel"
    bot_username = (await client.get_me()).username
    text = f"ꜰᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ʏᴏᴜʀ ᴅᴀᴛᴀʙᴀsᴇ ᴄʜᴀɴɴᴇʟ.\nᴍᴀᴋᴇ sᴜʀᴇ @{bot_username} ɪs ᴀᴅᴍɪɴ.\n\n/cancel"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_delete_db$"))
async def delete_db_channel(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "db_channel", None)
    await callback_query.answer("✅ Deleted.", show_alert=True)
    await db_channel_menu(client, callback_query)


# ==========================================================
# 🔹 CAPTION
# ==========================================================
@Client.on_callback_query(filters.regex("^u_caption$"))
async def caption_menu(client: Client, callback_query: CallbackQuery):
    from pyrogram.errors import MessageNotModified
    bot_username = (await client.get_me()).username
    caption = await db.get_custom_caption(bot_username)
    text = f"ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ʙᴏᴛ ɢɪᴠᴇɴ ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ.\n\nꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ - {caption or '{file_name}'}"
    buttons = [
        [InlineKeyboardButton("Set Caption", callback_data="u_set_caption")],
        [InlineKeyboardButton("Default Caption", callback_data="u_default_caption")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    try:
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    except MessageNotModified:
        pass


@Client.on_callback_query(filters.regex("^u_set_caption$"))
async def set_caption_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_caption"
    text = "sᴇɴᴅ ᴍᴇ ᴀ ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ.\n\nᴀᴠᴀɪʟᴀʙʟᴇ ғɪʟʟɪɴɢ:-\n{file_name}\n{file_size}\n{originalcaption}\n\n/cancel"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_caption")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^u_default_caption$"))
async def default_caption(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_custom_caption(bot_username)
    await callback_query.answer("✅ Default caption set.", show_alert=True)
    await caption_menu(client, callback_query)


# ==========================================================
# 🔹 BUTTONS
# ==========================================================
@Client.on_callback_query(filters.regex("^u_button$"))
async def button_menu(client: Client, callback_query: CallbackQuery):
    from pyrogram.errors import MessageNotModified
    bot_username = (await client.get_me()).username
    buttons_data = await db.get_custom_buttons(bot_username)
    text = "ʜᴇʀᴇ ʏᴏᴜ ᴄᴀɴ sᴇᴛ ᴀ ʙᴜᴛᴛᴏɴ ꜰᴏʀ ʏᴏᴜʀ ꜰɪʟᴇ.\n\nғᴏʀᴍᴀᴛ:\n[vj bot][buttonurl:https://t.me/vj_botz]"
    if buttons_data:
        buttons = [
            [InlineKeyboardButton("See Buttons", callback_data="u_see_buttons")],
            [InlineKeyboardButton("Remove Buttons", callback_data="u_remove_buttons")],
            [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
        ]
    else:
        buttons = [
            [InlineKeyboardButton("Add Buttons", callback_data="u_add_buttons")],
            [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
        ]
    try:
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    except MessageNotModified:
        pass


@Client.on_callback_query(filters.regex("^u_add_buttons$"))
async def add_buttons_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_buttons"
    text = "sᴇɴᴅ ᴍᴇ ᴀ ʙᴜᴛᴛᴏɴ:\n\n[Button Text][buttonurl:https://link.com]\n\n/cancel"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_button")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^u_see_buttons$"))
async def see_buttons(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    buttons_data = await db.get_custom_buttons(bot_username)
    text = "📋 **Current Buttons:**\n\n"
    for row in buttons_data:
        for btn in row:
            text += f"• `{btn['text']}` → {btn['url']}\n"
        text += "\n"
    back_buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_button")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(back_buttons))


@Client.on_callback_query(filters.regex("^u_remove_buttons$"))
async def remove_buttons(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_custom_buttons(bot_username)
    await callback_query.answer("✅ Buttons removed.", show_alert=True)
    await button_menu(client, callback_query)


# ==========================================================
# 🔹 AUTO DELETE
# ==========================================================
@Client.on_callback_query(filters.regex("^u_auto_delete$"))
async def auto_delete_menu(client: Client, callback_query: CallbackQuery):
    from pyrogram.errors import MessageNotModified
    bot_username = (await client.get_me()).username
    status = await db.get_auto_delete_status(bot_username)
    time_str = await db.get_auto_delete_time(bot_username)
    status_text = "ᴏɴ ✅" if status else "ᴏꜰꜰ ❌"
    text = (
        "♻️ **MESSAGE AUTO DELETE:**\n\n"
        "ᴍᴇssᴀɢᴇ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ: ɪғ ᴛɪᴍᴇ ɪs sᴇᴛ ᴛʜᴇɴ ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ "
        "ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ɢɪᴠᴇɴ ᴍᴇssᴀɢᴇ.\n\n"
        f"ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ - {status_text}\n\nᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ - {time_str}"
    )
    buttons = [
        [InlineKeyboardButton("Set Time", callback_data="u_set_autodel_time")],
        [InlineKeyboardButton("Auto Delete On/Off", callback_data="u_toggle_autodel")],
        [InlineKeyboardButton("Auto Delete Message", callback_data="u_autodel_msg")],
        [InlineKeyboardButton("Get Again File", callback_data="u_get_again")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    try:
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    except MessageNotModified:
        pass


@Client.on_callback_query(filters.regex("^u_set_autodel_time$"))
async def set_autodel_time(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_autodel_time"
    text = "sᴇɴᴅ ᴍᴇ ᴀ ᴛɪᴍᴇ - 1h ᴏʀ 15m\n\n/cancel"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_auto_delete")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^u_toggle_autodel$"))
async def toggle_autodel(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    current = await db.get_auto_delete_status(bot_username)
    await db.set_auto_delete_status(bot_username, not current)
    await callback_query.answer(f"Auto Delete {'ON ✅' if not current else 'OFF ❌'}", show_alert=True)
    await auto_delete_menu(client, callback_query)


@Client.on_callback_query(filters.regex("^u_get_again$"))
async def get_again_file(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    status = await db.get_auto_delete_status(bot_username)
    new_status = not status
    await db.set_auto_delete_status(bot_username, new_status)
    await callback_query.answer(f"Auto Delete {'ON ✅' if new_status else 'OFF ❌'}", show_alert=True)
    await auto_delete_menu(client, callback_query)


@Client.on_callback_query(filters.regex("^u_autodel_msg$"))
async def autodel_msg_menu(client: Client, callback_query: CallbackQuery):
    text = "📝 **AUTO DELETE MESSAGE:**\n\nᴄᴜsᴛᴏᴍɪsᴇ ʏᴏᴜʀ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ."
    buttons = [
        [InlineKeyboardButton("Auto Delete Text", callback_data="u_adtext")],
        [InlineKeyboardButton("Auto Delete Pic", callback_data="u_adpic")],
        [InlineKeyboardButton("Auto Delete Buttons", callback_data="u_adbuttons")],
        [InlineKeyboardButton("🔙 Back", callback_data="u_auto_delete")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^u_adtext$"))
async def adtext_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_adtext"
    text = "sᴇɴᴅ ᴍᴇ ᴀɴ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛᴇxᴛ.\n\n/cancel"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_autodel_msg")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^u_adpic$"))
async def adpic_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_adpic"
    text = "sᴇɴᴅ ᴍᴇ ᴀɴ ɪᴍᴀɢᴇ.\n\n/cancel"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_autodel_msg")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^u_adbuttons$"))
async def adbuttons_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_adbuttons"
    text = "sᴇɴᴅ ᴍᴇ ʙᴜᴛᴛᴏɴs:\n\n[Button Text][buttonurl:https://link.com]\n\n/cancel"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_autodel_msg")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 THUMBNAIL
# ==========================================================
@Client.on_callback_query(filters.regex("^u_thumbnail$"))
async def thumbnail_menu(client: Client, callback_query: CallbackQuery):
    from pyrogram.errors import MessageNotModified
    bot_username = (await client.get_me()).username
    thumb = await db.get_custom_thumbnail(bot_username)
    text = "🖼️ **CUSTOM THUMBNAIL:**\n\nᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ ғᴏʀ ᴠɪᴅᴇᴏ ғɪʟᴇ.\n\n"
    text += "✅ Thumbnail added." if thumb else "ʏᴏᴜ ᴅɪᴅɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ᴘɪᴄᴛᴜʀᴇ..."
    buttons = [
        [InlineKeyboardButton("Set Thumbnail", callback_data="u_set_thumb"),
         InlineKeyboardButton("View Thumbnail", callback_data="u_view_thumb")],
        [InlineKeyboardButton("Remove Thumbnail", callback_data="u_remove_thumb")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    try:
        await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    except MessageNotModified:
        pass


@Client.on_callback_query(filters.regex("^u_set_thumb$"))
async def set_thumb_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_thumb"
    text = "sᴇɴᴅ ᴍᴇ ᴀ ᴘɪᴄᴛᴜʀᴇ.\n\n/cancel"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_thumbnail")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^u_view_thumb$"))
async def view_thumb(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    thumb = await db.get_custom_thumbnail(bot_username)
    if not thumb:
        return await callback_query.answer("⚠️ No thumbnail set.", show_alert=True)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_thumbnail")]]
    await client.send_photo(callback_query.message.chat.id, photo=thumb, caption="🖼️ Current Thumbnail", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^u_remove_thumb$"))
async def remove_thumb(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    await db.delete_custom_thumbnail(bot_username)
    await callback_query.answer("✅ Thumbnail removed.", show_alert=True)
    await thumbnail_menu(client, callback_query)

@Client.on_message(filters.private & filters.text & ~filters.command(["cancel", "start"]), group=95)
async def receive_caption(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_caption":
        return
    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    await db.set_custom_caption(bot_username, message.text)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_caption")]]
    await message.reply_text("✅ Caption saved.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel", "start"]), group=96)
async def receive_buttons(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_buttons":
        return
    edit_states.pop(user_id, None)
    text = message.text.strip()
    pattern = r"\[([^\]]+)\]\[buttonurl:([^\]]+)\]"
    matches = re.findall(pattern, text)
    if not matches:
        return await message.reply_text("❌ Invalid format. Use: [Button Text][buttonurl:https://link.com]")
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
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_button")]]
    await message.reply_text("✅ Buttons saved.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel", "start"]), group=97)
async def receive_autodel_time(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_autodel_time":
        return
    text = message.text.strip().lower()
    if not (text.endswith("m") or text.endswith("h")):
        return await message.reply_text("❌ Invalid format. Use 15m or 1h.")
    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    await db.set_auto_delete_time(bot_username, text)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_auto_delete")]]
    await message.reply_text(f"✅ Time set to {text}", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel", "start"]), group=99)
async def receive_adtext(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_adtext":
        return
    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    await db.set_setting(f"adtext_{bot_username}", message.text)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_autodel_msg")]]
    await message.reply_text("✅ Auto delete text saved.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.photo, group=98)
async def receive_thumb(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_thumb":
        return
    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    await db.set_custom_thumbnail(bot_username, message.photo.file_id)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_thumbnail")]]
    await message.reply_text("✅ Thumbnail saved.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.photo, group=100)
async def receive_adpic(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_adpic":
        return
    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    await db.set_setting(f"adpic_{bot_username}", message.photo.file_id)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_autodel_msg")]]
    await message.reply_text("✅ Auto delete pic saved.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private, group=21)
async def receive_log_channel(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_log_channel":
        return
    if message.text and message.text.startswith("/"):
        edit_states.pop(user_id, None)
        return
    if not message.forward_from_chat:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
        return await message.reply_text("⚠️ Forward a message from the channel.", reply_markup=InlineKeyboardMarkup(buttons))
    chat = message.forward_from_chat
    bot_username = (await client.get_me()).username
    try:
        me = await client.get_me()
        member = await client.get_chat_member(chat.id, me.id)
        status_str = str(member.status).split(".")[-1].lower()
        if status_str not in ("administrator", "creator", "owner"):
            buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
            return await message.reply_text(f"⚠️ Bot is not admin in **{chat.title}**", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
        return await message.reply_text(f"⚠️ Error: `{type(e).__name__}: {e}`", reply_markup=InlineKeyboardMarkup(buttons))
    edit_states.pop(user_id, None)
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "log_channel", chat.id)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_log_channel")]]
    await message.reply_text(f"✅ **Log Channel Set:** {chat.title}", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private, group=22)
async def receive_db_channel(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_db_channel":
        return
    if message.text and message.text.startswith("/"):
        edit_states.pop(user_id, None)
        return
    if not message.forward_from_chat:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
        return await message.reply_text("⚠️ Forward a message from the channel.", reply_markup=InlineKeyboardMarkup(buttons))
    chat = message.forward_from_chat
    bot_username = (await client.get_me()).username
    try:
        me = await client.get_me()
        member = await client.get_chat_member(chat.id, me.id)
        status_str = str(member.status).split(".")[-1].lower()
        if status_str not in ("administrator", "creator", "owner"):
            buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
            return await message.reply_text(f"⚠️ Bot is not admin in **{chat.title}**", reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
        return await message.reply_text(f"⚠️ Error: `{type(e).__name__}: {e}`", reply_markup=InlineKeyboardMarkup(buttons))
    edit_states.pop(user_id, None)
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "db_channel", chat.id)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_db_channel")]]
    await message.reply_text(f"✅ **DB Channel Set:** {chat.title}", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel", "start"]), group=23)
async def receive_add_admin(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_add_admin":
        return
    try:
        new_admin = int(message.text.strip())
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
        return await message.reply_text("❌ Invalid ID.", reply_markup=InlineKeyboardMarkup(buttons))
    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        admins = clone_data.get("admins", [])
        if new_admin not in admins:
            admins.append(new_admin)
            await db.update_clone_setting(clone_data["user_id"], "admins", admins)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await message.reply_text(f"✅ Admin `{new_admin}` added.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.text & ~filters.command(["cancel", "start"]), group=24)
async def receive_remove_admin(client: Client, message: Message):
    user_id = message.from_user.id
    if edit_states.get(user_id) != "waiting_for_remove_admin":
        return
    try:
        rem_admin = int(message.text.strip())
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
        return await message.reply_text("❌ Invalid ID.", reply_markup=InlineKeyboardMarkup(buttons))
    edit_states.pop(user_id, None)
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        admins = clone_data.get("admins", [])
        if rem_admin in admins:
            admins.remove(rem_admin)
            await db.update_clone_setting(clone_data["user_id"], "admins", admins)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await message.reply_text(f"✅ Admin `{rem_admin}` removed.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.command("cancel") & filters.private, group=25)
async def cancel_clone_edit(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in edit_states:
        edit_states.pop(user_id, None)
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_settings")]]
        await message.reply_text("✅ Cancelled.", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^c_admins$"))
async def admins_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    admins = clone_data.get("admins", []) if clone_data else []
    text = f"👥 **ADMINS:**\n\n**Total Admins:** {len(admins)}"
    buttons = [
        [InlineKeyboardButton("Add Admin", callback_data="c_add_admin"),
         InlineKeyboardButton("Remove Admin", callback_data="c_remove_admin")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_add_admin$"))
async def add_admin_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_add_admin"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await callback_query.message.edit_text("👥 Send user ID to add as admin.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_remove_admin$"))
async def remove_admin_prompt(client: Client, callback_query: CallbackQuery):
    edit_states[callback_query.from_user.id] = "waiting_for_remove_admin"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_admins")]]
    await callback_query.message.edit_text("👥 Send user ID to remove.", reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_status$"))
async def bot_status(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    total_users = await db.users.count_documents({})
    banned_users = await db.banned_users.count_documents({})
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    up = int(time.time() - BOT_START_TIME)
    h, m, s = up // 3600, (up % 3600) // 60, up % 60
    text = (
        f"**{bot_username.upper()}**\n\n"
        f"USERS - {total_users}\n\n"
        f"BAN USERS - {banned_users}\n\n"
        f"CPU - {cpu}%\n\n"
        f"RAM - {ram}%\n\n"
        f"UPTIME - {h} Hours {m} Minutes {s} Seconds"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_settings")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_bot_mode$"))
async def bot_mode_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    current = clone_data.get("bot_mode", "public") if clone_data else "public"
    icon = "🌐" if current == "public" else "🔒"
    text = f"🛍️ **BOT MODE**\n\n{icon} Current: {current.title()}"
    buttons = [
        [InlineKeyboardButton("🌐 Public", callback_data="c_mode_public"),
         InlineKeyboardButton("🔒 Private", callback_data="c_mode_private")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_mode_(public|private)$"))
async def set_bot_mode(client: Client, callback_query: CallbackQuery):
    mode = callback_query.data.split("_")[-1]
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.update_clone_setting(clone_data["user_id"], "bot_mode", mode)
    await callback_query.answer(f"Mode: {mode.title()} ✅", show_alert=True)
    await bot_mode_menu(client, callback_query)


@Client.on_callback_query(filters.regex("^c_restart$"))
async def restart_bot(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("⏱️ Restarting...", show_alert=True)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_settings")]]
    await callback_query.message.edit_text("⏱️ **Restarting bot...**", reply_markup=InlineKeyboardMarkup(buttons))
    asyncio.create_task(_delayed_restart(client))


async def _delayed_restart(client: Client):
    await asyncio.sleep(3)
    try:
        await client.restart()
        print("✅ Restarted.")
    except Exception as e:
        print(f"⚠️ Restart error: {e}")


@Client.on_callback_query(filters.regex("^c_delete_bot$"))
async def delete_bot_prompt(client: Client, callback_query: CallbackQuery):
    text = "🚫 **DELETE BOT**\n\nAre you sure?"
    buttons = [
        [InlineKeyboardButton("❌ Cancel", callback_data="c_settings"),
         InlineKeyboardButton("🚫 Delete", callback_data="c_confirm_delete_bot")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_confirm_delete_bot$"))
async def confirm_delete_bot(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if clone_data:
        await db.delete_clone(clone_data["user_id"])
    await callback_query.message.edit_text("✅ Bot deleted.")


@Client.on_callback_query(filters.regex("^c_more_features$"))
async def more_features(client: Client, callback_query: CallbackQuery):
    text = "🔍 **MORE FEATURES**\n\n• /settings\n• /customize\n• /broadcast\n• /ban\n• /unban\n• /myplan\n• /link\n• /batch"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_settings")]]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^c_back$"))
async def clone_back_cb(client: Client, callback_query: CallbackQuery):
    from pyrogram.errors import MessageNotModified
    bot_username = (await client.get_me()).username
    bot_mention = f"@{bot_username}"
    user_mention = callback_query.from_user.mention
    clone_data = await db.get_clone_by_username(bot_username)
    start_text = clone_data.get("start_text") if clone_data else None
    start_buttons = clone_data.get("start_buttons", []) if clone_data else []
    if not start_text:
        start_text = "ʜᴇʏ {mention} 👋,\n\nᴍʏ ɴᴀᴍᴇ ɪs {bot_mention}\n\nɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴀɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ."
    try:
        formatted = start_text.format(mention=user_mention, bot_mention=bot_mention)
    except Exception:
        formatted = start_text
    keyboard = []
    for btn in start_buttons:
        keyboard.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
    if not keyboard:
        keyboard = [
            [InlineKeyboardButton("Help", callback_data="c_help"),
             InlineKeyboardButton("About", callback_data="c_about")],
            [InlineKeyboardButton("Settings", callback_data="c_settings"),
             InlineKeyboardButton("Customize", url=f"https://t.me/{bot_username}?start=customize")],
            [InlineKeyboardButton("Update", url="https://t.me/YourChannel"),
             InlineKeyboardButton("Support", url="https://t.me/YourSupport")]
        ]
    try:
        await callback_query.message.edit_text(formatted, reply_markup=InlineKeyboardMarkup(keyboard))
    except MessageNotModified:
        pass


@Client.on_callback_query(filters.regex("^c_plan$"))
async def c_plan_callback(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    plan_text = await db.get_premium_plan_text(bot_username)
    if not plan_text:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await callback_query.message.edit_text("❌ **Plan Not Available**", reply_markup=InlineKeyboardMarkup(buttons))
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await callback_query.message.edit_text(f"💎 **PREMIUM PLAN**\n\n{plan_text}", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)


@Client.on_callback_query(filters.regex("^c_myplan$"))
async def c_myplan_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    bot_username = (await client.get_me()).username
    is_premium = await db.is_premium_user(user_id, bot_username)
    text = "💎 **My Premium Status**\n\n✅ Premium (Active)" if is_premium else "💎 **My Premium Status**\n\n📌 Free\n🆓 Limit: 5 files/day"
    buttons = [
        [InlineKeyboardButton("💎 View Plans", callback_data="c_plan")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_back")]
    ]
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private & filters.regex(r"^/start verify_(\d+)$"), group=4)
async def handle_verify_callback(client: Client, message: Message):
    user_id = int(message.matches[0].group(1))
    bot_username = (await client.get_me()).username
    from utils.verify_helper import mark_verified
    await mark_verified(user_id, bot_username)
    await message.reply_text("✅ **Verification Complete!**")


@Client.on_callback_query(filters.regex("^fsub_check$"))
async def fsub_check(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    from utils.fsub_helper import check_subscription
    not_joined = await check_subscription(client, callback_query.from_user.id, bot_username)
    if not not_joined:
        await callback_query.answer("✅ Verified!", show_alert=True)
        try:
            await callback_query.message.delete()
        except Exception:
            pass
        await callback_query.message.reply_text("✅ **Verification Complete!**")
    else:
        await callback_query.answer("⚠️ You haven't joined all channels yet.", show_alert=True)


@Client.on_callback_query(filters.regex("^u_(free_limit|refer|permanent_link|protect_content)$"))
async def user_setting_handler(client: Client, callback_query: CallbackQuery):
    key = callback_query.data.replace("u_", "")
    messages = {
        "free_limit": "🆓 Free usage: 5 files per day.",
        "refer": "🌍 Refer & Earn: Coming soon!",
        "permanent_link": "♾️ Permanent Link: Toggle.",
        "protect_content": "🔒 Protect Content: Toggle."
    }
    await callback_query.answer(messages.get(key, "Coming soon"), show_alert=True)


@Client.on_message(filters.command("broadcast") & filters.private)
async def clone_broadcast(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if not clone_data or clone_data["user_id"] != user_id:
        return await message.reply_text("❌ Owner only.")
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a message.")
    users = await db.get_all_users()
    status = await message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    success = 0
    for u in users:
        try:
            await message.reply_to_message.copy(u["user_id"])
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await status.edit_text(f"✅ Sent to {success}/{len(users)} users.")


@Client.on_message(filters.command("ban") & filters.private)
async def clone_ban(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if not clone_data or clone_data["user_id"] != user_id:
        return await message.reply_text("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /ban [user_id]")
    try:
        target = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid ID.")
    await db.ban_user(target)
    await message.reply_text(f"✅ User {target} banned.")


@Client.on_message(filters.command("unban") & filters.private)
async def clone_unban(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if not clone_data or clone_data["user_id"] != user_id:
        return await message.reply_text("❌ Owner only.")
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Usage: /unban [user_id]")
    try:
        target = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid ID.")
    await db.unban_user(target)
    await message.reply_text(f"✅ User {target} unbanned.")
