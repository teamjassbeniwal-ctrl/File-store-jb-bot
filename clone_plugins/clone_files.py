# clone_plugins/clone_files.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from utils.shortener import shorten_url
from utils.verify_helper import needs_verification, mark_verified
from utils.fsub_helper import check_subscription, build_fsub_keyboard
from utils.fsub_middleware import check_force_sub
import asyncio
import base64
import time

user_states = {}


# ==========================================================
# 🔹 AUTO DELETE HELPER
# ==========================================================
async def _auto_delete_file(client: Client, message, seconds: int):
    print(f"⏱️ Auto-delete: waiting {seconds}s")
    await asyncio.sleep(seconds)
    try:
        # Send alert
        try:
            alert = await message.reply_text(
                "⚠️ **This file has been auto-deleted** due to copyright protection."
            )
            await asyncio.sleep(10)
            await alert.delete()
        except Exception:
            pass
        # Delete file
        await message.delete()
        print("✅ Auto-delete: file deleted.")
    except Exception as e:
        print(f"⚠️ Auto-delete failed: {type(e).__name__}: {e}")


# ==========================================================
# 🔹 /link
# ==========================================================
@Client.on_message(filters.command("link") & filters.private)
async def clone_link(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return

    user_states[message.from_user.id] = "waiting_for_link_file"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(
        "sᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴛᴏʀᴇ",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 /batch
# ==========================================================
@Client.on_message(filters.command("batch") & filters.private)
async def clone_batch(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return

    user_states[message.from_user.id] = "waiting_for_batch_file"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(
        "𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗧𝗵𝗲 𝗙𝗶𝗿𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗙𝗿𝗼𝗺 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗖𝗵𝗮𝗻𝗻𝗲𝗹\n\n"
        f"ɴᴏᴛᴇ : ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜɪs @{bot_username} ɪs ᴀᴅᴍɪɴ",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 HANDLE SINGLE FILE FOR /link (with proper thumbnail)
# ==========================================================
@Client.on_message(
    filters.private &
    (filters.document | filters.video | filters.photo | filters.audio |
     filters.voice | filters.video_note | filters.animation | filters.text),
    group=1
)
async def handle_clone_link(client: Client, message: Message):
    user_id = message.from_user.id
    if user_states.get(user_id) != "waiting_for_link_file":
        return
    if message.text and message.text.startswith("/"):
        return
    user_states.pop(user_id, None)

    bot_username = (await client.get_me()).username

    # Force Sub gate
    fsub_status = await db.get_fsub_status(bot_username)
    if fsub_status:
        not_joined = await check_subscription(client, user_id, bot_username)
        if not_joined:
            fsub_text = await db.get_fsub_text(bot_username)
            fsub_img = await db.get_fsub_image(bot_username)
            keyboard = await build_fsub_keyboard(client, bot_username, not_joined)
            msg_text = fsub_text or "📢 **Please Join Our Channels**"
            if fsub_img:
                await message.reply_photo(photo=fsub_img, caption=msg_text, reply_markup=keyboard)
            else:
                await message.reply_text(msg_text, reply_markup=keyboard, disable_web_page_preview=True)
            return

    # Verification gate
    if await needs_verification(user_id, bot_username):
        v_url = await db.get_verify_shortlink_url(bot_username)
        v_api = await db.get_verify_shortlink_api(bot_username)
        tutorial = await db.get_verify_tutorial(bot_username)
        direct = f"https://telegram.me/{bot_username}?start=verify_{user_id}"
        short = await shorten_url(v_url, v_api, direct) if v_url and v_api else direct
        buttons = []
        if short:
            buttons.append([InlineKeyboardButton("✅ Verify Now", url=short)])
        if tutorial:
            buttons.append([InlineKeyboardButton("📺 Tutorial", url=tutorial)])
        buttons.append([InlineKeyboardButton("💎 Get Premium", callback_data="premium")])
        return await message.reply_text(
            f"ʜᴇʏ {message.from_user.first_name}\n\nʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪꜰɪᴇᴅ ᴛᴏᴅᴀʏ 😐\n#ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ:- 1/2",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

    # File processing
    file_id = None
    media_type = None

    if message.document:
        file_id = message.document.file_id
        media_type = "document"
    elif message.video:
        file_id = message.video.file_id
        media_type = "video"
    elif message.photo:
        file_id = message.photo.file_id
        media_type = "photo"
    elif message.audio:
        file_id = message.audio.file_id
        media_type = "audio"
    elif message.voice:
        file_id = message.voice.file_id
        media_type = "voice"
    elif message.video_note:
        file_id = message.video_note.file_id
        media_type = "video_note"
    elif message.animation:
        file_id = message.animation.file_id
        media_type = "animation"
    elif message.text:
        file_id = f"text:{message.text}"
        media_type = "text"

    if not file_id:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await message.reply_text("❌ Unsupported file type.", reply_markup=InlineKeyboardMarkup(buttons))

    raw_id = f"{user_id}_{message.id}_{int(time.time())}"
    unique_id = base64.urlsafe_b64encode(raw_id.encode()).decode().rstrip("=")

    await db.save_stored_file(unique_id, file_id, message.id, message.chat.id, user_id, "single")

    direct_link = f"https://telegram.me/{bot_username}?start={unique_id}"
    sl_status = await db.get_shortlink_status(bot_username)
    sl_url = await db.get_shortlink_url(bot_username)
    sl_api = await db.get_shortlink_api(bot_username)

    final_link = direct_link
    if sl_status and sl_url and sl_api:
        short = await shorten_url(sl_url, sl_api, direct_link)
        if short:
            final_link = short

    # Get custom settings
    caption = await db.get_custom_caption(bot_username) or "📁 **Here is your file**"
    buttons_data = await db.get_custom_buttons(bot_username)
    thumb = await db.get_custom_thumbnail(bot_username)
    autodel_status = await db.get_auto_delete_status(bot_username)
    autodel_time = await db.get_auto_delete_time(bot_username)

    # Replace caption placeholders
    if message.document:
        caption = caption.replace("{file_name}", message.document.file_name or "file")
        if message.document.file_size:
            caption = caption.replace("{file_size}", f"{round(message.document.file_size / 1024 / 1024, 2)} MB")
    elif message.video:
        caption = caption.replace("{file_name}", message.video.file_name or "video")
        if message.video.file_size:
            caption = caption.replace("{file_size}", f"{round(message.video.file_size / 1024 / 1024, 2)} MB")
    elif message.audio:
        caption = caption.replace("{file_name}", message.audio.file_name or "audio")

    # Build keyboard
    keyboard = []
    for row in buttons_data:
        kb_row = []
        for btn in row:
            kb_row.append(InlineKeyboardButton(btn["text"], url=btn["url"]))
        keyboard.append(kb_row)

    keyboard.append([InlineKeyboardButton("🔗 Open Link", url=final_link)])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="c_back")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # ==========================================================
    # 🔹 SEND WITH PROPER METHOD (thumbnail support)
    # ==========================================================
    try:
        sent = None

        if media_type == "video":
            sent = await client.send_video(
                chat_id=message.chat.id,
                video=file_id,
                caption=caption,
                thumb=thumb,
                reply_markup=reply_markup
            )
        elif media_type == "document":
            sent = await client.send_document(
                chat_id=message.chat.id,
                document=file_id,
                caption=caption,
                thumb=thumb,
                reply_markup=reply_markup
            )
        elif media_type == "audio":
            sent = await client.send_audio(
                chat_id=message.chat.id,
                audio=file_id,
                caption=caption,
                thumb=thumb,
                reply_markup=reply_markup
            )
        elif media_type == "animation":
            sent = await client.send_animation(
                chat_id=message.chat.id,
                animation=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        elif media_type == "photo":
            sent = await client.send_photo(
                chat_id=message.chat.id,
                photo=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        elif media_type == "voice":
            sent = await client.send_voice(
                chat_id=message.chat.id,
                voice=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        elif media_type == "video_note":
            sent = await client.send_video_note(
                chat_id=message.chat.id,
                video_note=file_id
            )
        elif media_type == "text":
            sent = await client.send_message(
                chat_id=message.chat.id,
                text=message.text,
                reply_markup=reply_markup
            )

        # Delete original
        try:
            await message.delete()
        except Exception:
            pass

        # ==========================================================
        # 🔹 AUTO DELETE — schedule
        # ==========================================================
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
                print(f"⏱️ Scheduling auto-delete in {seconds}s for user {user_id}")
                asyncio.create_task(_auto_delete_file(client, sent, seconds))
            except Exception as e:
                print(f"⚠️ Auto-delete scheduling error: {e}")

    except Exception as e:
        print(f"File send error: {type(e).__name__}: {e}")
        await message.reply_text(
            f"✅ **File Stored!**\n\n🔗 **Link:**\n`{final_link}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Open Link", url=final_link)],
                [InlineKeyboardButton("🔙 Back", callback_data="c_back")]
            ])
            )

# ==========================================================
# 🔹 HANDLE BATCH FILE
# ==========================================================
@Client.on_message(filters.private, group=2)
async def handle_clone_batch(client: Client, message: Message):
    user_id = message.from_user.id
    if user_states.get(user_id) != "waiting_for_batch_file":
        return
    if message.text and message.text.startswith("/"):
        return
    if not message.forward_from_chat and not message.forward_from:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await message.reply_text(
            "⚠️ Please forward a message from your batch channel.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    user_states.pop(user_id, None)
    from_chat_id = None
    if message.forward_from_chat:
        from_chat_id = message.forward_from_chat.id
    elif message.forward_from:
        from_chat_id = message.forward_from.id

    start_id = message.forward_from_message_id or message.id

    user_states[user_id] = {
        "state": "waiting_for_batch_count",
        "from_chat_id": from_chat_id,
        "start_id": start_id
    }

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(
        "📦 **How many files?** Send a number.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 HANDLE BATCH COUNT
# ==========================================================
@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=3)
async def handle_clone_batch_count(client: Client, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if not isinstance(state, dict) or state.get("state") != "waiting_for_batch_count":
        return

    try:
        count = int(message.text.strip())
        if count < 1 or count > 500:
            raise ValueError
    except ValueError:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        return await message.reply_text("⚠️ Invalid number (1-500).", reply_markup=InlineKeyboardMarkup(buttons))

    bot_username = (await client.get_me()).username

    # Force Sub gate
    fsub_status = await db.get_fsub_status(bot_username)
    if fsub_status:
        not_joined = await check_subscription(client, user_id, bot_username)
        if not_joined:
            fsub_text = await db.get_fsub_text(bot_username)
            fsub_img = await db.get_fsub_image(bot_username)
            keyboard = await build_fsub_keyboard(client, bot_username, not_joined)
            msg_text = fsub_text or "📢 **Please Join Our Channels**"
            if fsub_img:
                await message.reply_photo(photo=fsub_img, caption=msg_text, reply_markup=keyboard)
            else:
                await message.reply_text(msg_text, reply_markup=keyboard, disable_web_page_preview=True)
            return

    # Verification gate
    if await needs_verification(user_id, bot_username):
        v_url = await db.get_verify_shortlink_url(bot_username)
        v_api = await db.get_verify_shortlink_api(bot_username)
        tutorial = await db.get_verify_tutorial(bot_username)
        direct = f"https://telegram.me/{bot_username}?start=verify_{user_id}"
        short = await shorten_url(v_url, v_api, direct) if v_url and v_api else direct
        buttons = []
        if short:
            buttons.append([InlineKeyboardButton("✅ Verify Now", url=short)])
        if tutorial:
            buttons.append([InlineKeyboardButton("📺 Tutorial", url=tutorial)])
        return await message.reply_text(
            f"ʜᴇʏ {message.from_user.first_name}\n\nʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪꜰɪᴇᴅ ᴛᴏᴅᴀʏ 😐\n#ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ:- 1/2",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

    from_chat_id = state["from_chat_id"]
    start_id = state["start_id"]
    user_states.pop(user_id, None)

    raw_id = f"batch_{user_id}_{start_id}_{int(time.time())}"
    unique_id = base64.urlsafe_b64encode(raw_id.encode()).decode().rstrip("=")

    await db.save_batch(unique_id, from_chat_id, start_id, count, user_id)

    direct_link = f"https://telegram.me/{bot_username}?start={unique_id}"
    sl_status = await db.get_shortlink_status(bot_username)
    sl_url = await db.get_shortlink_url(bot_username)
    sl_api = await db.get_shortlink_api(bot_username)

    final_link = direct_link
    if sl_status and sl_url and sl_api:
        short = await shorten_url(sl_url, sl_api, direct_link)
        if short:
            final_link = short

    buttons = [
        [InlineKeyboardButton("🔗 Open Batch", url=final_link)],
        [InlineKeyboardButton("🔙 Back", callback_data="c_back")]
    ]
    await message.reply_text(
        f"✅ **Batch Stored!**\n\n📦 Files: `{count}`\n🔗 **Link:** `{final_link}`",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )


# ==========================================================
# 🔹 VERIFICATION CALLBACK
# ==========================================================
@Client.on_message(filters.private & filters.regex(r"^/start verify_(\d+)$"), group=4)
async def handle_verify_callback(client: Client, message: Message):
    user_id = int(message.matches[0].group(1))
    bot_username = (await client.get_me()).username
    await mark_verified(user_id, bot_username)
    await message.reply_text("✅ **Verification Complete!**")


# ==========================================================
# 🔹 CANCEL
# ==========================================================
@Client.on_message(filters.command("cancel") & filters.private)
async def clone_cancel(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states:
        user_states.pop(user_id, None)
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
        await message.reply_text("✅ Cancelled.", reply_markup=InlineKeyboardMarkup(buttons))
        
