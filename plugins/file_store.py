# plugins/file_store.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import base64
import time

# Temporary storage for user states
# (For real production, use a proper conversation handler or MongoDB state)
user_states = {}


# ==========================================================
# 🔹 /link COMMAND
# ==========================================================
@Client.on_message(filters.command("link") & filters.private)
async def link_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_link_file"

    await message.reply_text(
        "sᴇɴᴅ ᴍᴇ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴛᴏʀᴇ"
    )


# ==========================================================
# 🔹 HANDLE FILE FOR /link
# ==========================================================
@Client.on_message(
    filters.private &
    (filters.document | filters.video | filters.photo | filters.audio | filters.voice | filters.video_note | filters.animation | filters.text),
    group=1
)
async def handle_link_file(client: Client, message: Message):
    user_id = message.from_user.id

    # Only handle if the user is in /link state
    if user_states.get(user_id) != "waiting_for_link_file":
        return

    # Skip commands
    if message.text and message.text.startswith("/"):
        return

    user_states.pop(user_id, None)

    # Get file_id
    file_id = None
    if message.document:
        file_id = message.document.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.photo:
        file_id = message.photo.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.voice:
        file_id = message.voice.file_id
    elif message.video_note:
        file_id = message.video_note.file_id
    elif message.animation:
        file_id = message.animation.file_id
    elif message.text:
        file_id = f"text:{message.text}"

    if not file_id:
        return await message.reply_text("❌ Unsupported file type.")

    # Generate unique ID
    raw_id = f"{user_id}_{message.id}_{int(time.time())}"
    unique_id = base64.urlsafe_b64encode(raw_id.encode()).decode().rstrip("=")

    # Save to DB
    await db.db.stored_files.insert_one({
        "unique_id": unique_id,
        "file_id": file_id,
        "message_id": message.id,
        "chat_id": message.chat.id,
        "owner_id": user_id,
        "type": "single"
    })

    # Get bot username
    bot_username = (await client.get_me()).username
    share_link = f"https://telegram.me/{bot_username}?start={unique_id}"

    # Check if user has shortlink enabled
    user = await db.get_user(user_id)
    shortlink_enabled = user.get("shortlink", False) if user else False

    if shortlink_enabled:
        # Integrate your shortlink API here
        # share_link = await shorten_url(share_link)
        pass

    await message.reply_text(
        f"✅ **File Stored Successfully!**\n\n"
        f"🔗 **Shareable Link:**\n`{share_link}`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Open Link", url=share_link)]
        ])
    )


# ==========================================================
# 🔹 /batch COMMAND
# ==========================================================
@Client.on_message(filters.command("batch") & filters.private)
async def batch_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_batch_file"

    bot_username = (await client.get_me()).username

    text = (
        "𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗧𝗵𝗲 𝗙𝗶𝗿𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗙𝗿𝗼𝗺 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 (𝗪𝗶𝘁𝗵 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗧𝗮𝗴).. 𝗢𝗿 𝗚𝗶𝘃𝗲 𝗠𝗲 𝗙𝗶𝗿𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗟𝗶𝗻𝗸 𝗙𝗿𝗼𝗺 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗖𝗵𝗮𝗻𝗻𝗲𝗹\n\n"
        f"ɴᴏᴛᴇ : ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜɪs @{bot_username}  ʙᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜ ғᴜʟʟ ʀɪɢʜᴛ"
    )
    await message.reply_text(text)


# ==========================================================
# 🔹 HANDLE BATCH FILE
# ==========================================================
@Client.on_message(filters.private, group=2)
async def handle_batch_file(client: Client, message: Message):
    user_id = message.from_user.id

    # Only handle if the user is in /batch state
    if user_states.get(user_id) != "waiting_for_batch_file":
        return

    if message.text and message.text.startswith("/"):
        return

    # Check for forwarded message
    if not message.forward_from_chat and not message.forward_from:
        return await message.reply_text(
            "⚠️ Please forward a message from your batch channel."
        )

    user_states.pop(user_id, None)

    # Determine chat_id and first message id
    from_chat_id = None
    if message.forward_from_chat:
        from_chat_id = message.forward_from_chat.id
    elif message.forward_from:
        from_chat_id = message.forward_from.id

    start_id = message.forward_from_message_id or message.id

    # Ask for count
    user_states[user_id] = {
        "state": "waiting_for_batch_count",
        "from_chat_id": from_chat_id,
        "start_id": start_id
    }

    await message.reply_text(
        "📦 **How many files are in this batch?**\n\n"
        "Send a number (e.g., `50`).\n"
        "Send /cancel to cancel."
    )


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
        if count < 1 or count > 500:
            raise ValueError
    except ValueError:
        return await message.reply_text("⚠️ Invalid number. Please send a number between 1 and 500.")

    from_chat_id = state["from_chat_id"]
    start_id = state["start_id"]
    user_states.pop(user_id, None)

    # Generate unique ID
    raw_id = f"batch_{user_id}_{start_id}_{int(time.time())}"
    unique_id = base64.urlsafe_b64encode(raw_id.encode()).decode().rstrip("=")

    # Save batch to DB
    await db.db.stored_files.insert_one({
        "unique_id": unique_id,
        "from_chat_id": from_chat_id,
        "start_id": start_id,
        "count": count,
        "owner_id": user_id,
        "type": "batch"
    })

    bot_username = (await client.get_me()).username
    share_link = f"https://telegram.me/{bot_username}?start={unique_id}"

    await message.reply_text(
        f"✅ **Batch Stored!**\n\n"
        f"📦 Files: `{count}`\n"
        f"🔗 **Link:** `{share_link}`",
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

    # Look up the stored file
    stored = await db.db.stored_files.find_one({"unique_id": payload})

    if not stored:
        return await message.reply_text("❌ Invalid or expired link.")

    if stored["type"] == "single":
        file_id = stored["file_id"]
        if file_id.startswith("text:"):
            await message.reply_text(file_id.replace("text:", ""))
        else:
            await message.reply_cached_media(
                file_id,
                caption="📁 **Here is your file**"
            )

    elif stored["type"] == "batch":
        from_chat_id = stored["from_chat_id"]
        start_id = stored["start_id"]
        count = stored["count"]

        await message.reply_text(f"📦 Sending {count} files...")

        for i in range(count):
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=from_chat_id,
                    message_id=start_id + i
                )
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
