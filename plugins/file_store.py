# plugins/file_store.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import base64
import time

user_states = {}


# ==========================================================
# 🔹 /link COMMAND
# ==========================================================
@Client.on_message(filters.command("link") & filters.private)
async def link_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_link_file"
    await message.reply_text("sᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴛᴏʀᴇ")


# ==========================================================
# 🔹 /batch COMMAND
# ==========================================================
@Client.on_message(filters.command("batch") & filters.private)
async def batch_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_batch_file"
    bot_username = (await client.get_me()).username

    await message.reply_text(
        "𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗧𝗵𝗲 𝗙𝗶𝗿𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗙𝗿𝗼𝗺 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 (𝗪𝗶𝘁𝗵 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗧𝗮𝗴).. 𝗢𝗿 𝗚𝗶𝘃𝗲 𝗠𝗲 𝗙𝗶𝗿𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗟𝗶𝗻𝗸 𝗙𝗿𝗼𝗺 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗖𝗵𝗮𝗻𝗻𝗲𝗹\n\n"
        f"ɴᴏᴛᴇ : ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜɪs @{bot_username}  ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜ ғᴜʟʟ ʀɪɢʜᴛ"
    )


# ==========================================================
# 🔹 /custom_batch COMMAND
# ==========================================================
@Client.on_message(filters.command("custom_batch") & filters.private)
async def custom_batch_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_custom_batch"

    await message.reply_text(
        "📝 **CUSTOM BATCH**\n\n"
        "Send me the message links you want to store.\n\n"
        "Format: One link per line\n"
        "Example:\n"
        "`https://t.me/channel/123`\n"
        "`https://t.me/channel/124`"
    )


# ==========================================================
# 🔹 /multiple_batch COMMAND
# ==========================================================
@Client.on_message(filters.command("multiple_batch") & filters.private)
async def multiple_batch_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_multiple_batch"

    await message.reply_text(
        "📦 **MULTIPLE BATCH**\n\n"
        "Send me multiple channel messages (one per line).\n"
        "I will generate separate batch links for each."
    )


# ==========================================================
# 🔹 /special_link COMMAND
# ==========================================================
@Client.on_message(filters.command("special_link") & filters.private)
async def special_link_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_special_link"

    await message.reply_text(
        "✨ **SPECIAL LINK**\n\n"
        "Send me the file/message you want to store with custom settings.\n\n"
        "Custom settings include: no shortlink, no auto-delete, custom caption."
    )


# ==========================================================
# 🔹 HANDLE SINGLE FILE FOR /link
# ==========================================================
@Client.on_message(
    filters.private &
    (filters.document | filters.video | filters.photo | filters.audio | filters.voice | filters.video_note | filters.animation | filters.text),
    group=1
)
async def handle_link_file(client: Client, message: Message):
    user_id = message.from_user.id
    if user_states.get(user_id) != "waiting_for_link_file":
        return
    if message.text and message.text.startswith("/"):
        return

    user_states.pop(user_id, None)

    file_id = None
    if message.document: file_id = message.document.file_id
    elif message.video: file_id = message.video.file_id
    elif message.photo: file_id = message.photo.file_id
    elif message.audio: file_id = message.audio.file_id
    elif message.voice: file_id = message.voice.file_id
    elif message.video_note: file_id = message.video_note.file_id
    elif message.animation: file_id = message.animation.file_id
    elif message.text: file_id = f"text:{message.text}"

    if not file_id:
        return await message.reply_text("❌ Unsupported file type.")

    raw_id = f"{user_id}_{message.id}_{int(time.time())}"
    unique_id = base64.urlsafe_b64encode(raw_id.encode()).decode().rstrip("=")

    await db.save_stored_file(
        unique_id=unique_id,
        file_id=file_id,
        message_id=message.id,
        chat_id=message.chat.id,
        owner_id=user_id,
        file_type="single"
    )

    bot_username = (await client.get_me()).username
    share_link = f"https://telegram.me/{bot_username}?start={unique_id}"

    await message.reply_text(
        f"✅ **File Stored Successfully!**\n\n"
        f"🔗 **Shareable Link:**\n`{share_link}`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Open Link", url=share_link)]
        ])
    )


# ==========================================================
# 🔹 HANDLE BATCH FILE
# ==========================================================
@Client.on_message(filters.private, group=2)
async def handle_batch_file(client: Client, message: Message):
    user_id = message.from_user.id
    if user_states.get(user_id) != "waiting_for_batch_file":
        return
    if message.text and message.text.startswith("/"):
        return
    if not message.forward_from_chat and not message.forward_from:
        return await message.reply_text("⚠️ Please forward a message from your batch channel.")

    user_states.pop(user_id, None)

    from_chat_id = None
    if message.forward_from_chat: from_chat_id = message.forward_from_chat.id
    elif message.forward_from: from_chat_id = message.forward_from.id

    start_id = message.forward_from_message_id or message.id

    user_states[user_id] = {
        "state": "waiting_for_batch_count",
        "from_chat_id": from_chat_id,
        "start_id": start_id
    }

    await message.reply_text("📦 **How many files are in this batch?**\n\nSend a number (e.g., `50`).")


# ==========================================================
# 🔹 HANDLE BATCH COUNT
# ==========================================================
@Client.on_message(filters.private & filters.text & ~filters.command(["cancel"]), group=3)
async def handle_batch_count(client: Client, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    if not isinstance(state, dict) or state.get("state") != "waiting_for_batch_count":
        return

    try:
        count = int(message.text.strip())
        if count < 1 or count > 500: raise ValueError
    except ValueError:
        return await message.reply_text("⚠️ Invalid number (1-500).")

    from_chat_id = state["from_chat_id"]
    start_id = state["start_id"]
    user_states.pop(user_id, None)

    raw_id = f"batch_{user_id}_{start_id}_{int(time.time())}"
    unique_id = base64.urlsafe_b64encode(raw_id.encode()).decode().rstrip("=")

    await db.save_batch(unique_id, from_chat_id, start_id, count, user_id)

    bot_username = (await client.get_me()).username
    share_link = f"https://telegram.me/{bot_username}?start={unique_id}"

    await message.reply_text(
        f"✅ **Batch Stored!**\n\n📦 Files: `{count}`\n🔗 **Link:** `{share_link}`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Open Batch", url=share_link)]
        ])
    )


# ==========================================================
# 🔹 RETRIEVE FILE VIA DEEP LINK
# ==========================================================
@Client.on_message(filters.private & filters.regex(r"^/start (?!customize)(.+)"))
async def retrieve_file(client: Client, message: Message):
    payload = message.text.split(" ", 1)[1].strip()
    stored = await db.get_stored_file(payload)

    if not stored:
        return await message.reply_text("❌ Invalid or expired link.")

    if stored["type"] == "single":
        file_id = stored["file_id"]
        if file_id.startswith("text:"):
            await message.reply_text(file_id.replace("text:", ""))
        else:
            await message.reply_cached_media(file_id, caption="📁 **Here is your file**")

    elif stored["type"] == "batch":
        from_chat_id = stored["from_chat_id"]
        start_id = stored["start_id"]
        count = stored["count"]
        await message.reply_text(f"📦 Sending {count} files...")
        for i in range(count):
            try:
                await client.copy_message(chat_id=message.chat.id, from_chat_id=from_chat_id, message_id=start_id + i)
            except Exception as e:
                print(f"Failed to copy {start_id + i}: {e}")


# ==========================================================
# 🔹 CANCEL COMMAND
# ==========================================================
@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_states:
        user_states.pop(user_id, None)
        await message.reply_text("✅ Cancelled.")
    else:
        await message.reply_text("Nothing to cancel.")
