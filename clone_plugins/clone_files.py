# clone_plugins/clone_files.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import base64
import time

# 🔹 STORE SINGLE FILE
@Client.on_message(filters.command("link") & filters.private)
async def store_file(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a file/message to store it.")
    
    file_msg = message.reply_to_message
    file_id = None
    
    if file_msg.document:
        file_id = file_msg.document.file_id
    elif file_msg.video:
        file_id = file_msg.video.file_id
    elif file_msg.photo:
        file_id = file_msg.photo.file_id
    elif file_msg.audio:
        file_id = file_msg.audio.file_id
    
    if not file_id:
        return await message.reply_text("❌ Unsupported file type.")
    
    # Generate a unique ID
    raw_id = f"{message.from_user.id}{file_msg.id}{time.time()}"
    unique_id = base64.urlsafe_b64encode(raw_id.encode()).decode()[:12]
    
    # Save to DB
    await db.save_file(file_id, unique_id, file_msg.id)
    
    # Get bot username dynamically
    bot_username = (await client.get_me()).username
    share_link = f"https://t.me/{bot_username}?start={unique_id}"
    
    await message.reply_text(
        f"✅ **File Stored Successfully!**\n\n"
        f"🔗 **Shareable Link:**\n`{share_link}`\n\n"
        f"📌 Click the link to access the file anytime.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Open Link", url=share_link)]
        ])
    )


# 🔹 STORE BATCH FILES
@Client.on_message(filters.command("batch") & filters.private)
async def store_batch(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to the first message of the batch.")
    
    # Get the range (e.g., /batch 5)
    try:
        count = int(message.command[1])
    except (IndexError, ValueError):
        return await message.reply_text("⚠️ Usage: `/batch <number>` (reply to the first message)")
    
    start_id = message.reply_to_message.id
    bot_username = (await client.get_me()).username
    
    # Generate a unique ID for this batch
    raw_id = f"batch_{message.from_user.id}_{start_id}_{time.time()}"
    unique_id = base64.urlsafe_b64encode(raw_id.encode()).decode()[:12]
    
    # Save batch reference to DB
    await db.db.batches.insert_one({
        "unique_id": unique_id,
        "chat_id": message.chat.id,
        "start_id": start_id,
        "count": count,
        "owner_id": message.from_user.id
    })
    
    share_link = f"https://t.me/{bot_username}?start={unique_id}"
    
    await message.reply_text(
        f"✅ **Batch Stored!**\n\n"
        f"📦 Files: `{count}`\n"
        f"🔗 **Link:** `{share_link}`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Open Batch", url=share_link)]
        ])
    )


# 🔹 HANDLE DEEP LINK FOR FILES (Triggered from clone_start.py)
@Client.on_message(filters.private & filters.regex(r"^/start (?!customize)(.+)"))
async def retrieve_file(client: Client, message: Message):
    payload = message.text.split(" ", 1)[1]
    
    # Check if it's a batch
    batch_data = await db.db.batches.find_one({"unique_id": payload})
    if batch_data:
        start_id = batch_data['start_id']
        count = batch_data['count']
        chat_id = batch_data['chat_id']
        
        await message.reply_text(f"📦 Sending {count} files...")
        for i in range(count):
            try:
                await client.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=chat_id,
                    message_id=start_id + i
                )
            except Exception as e:
                print(f"Error copying message {start_id + i}: {e}")
        return
    
    # Check if it's a single file
    file_data = await db.get_file(payload)
    if file_data:
        await message.reply_cached_media(
            file_data['file_id'],
            caption="📁 **Here is your file**"
        )
    else:
        await message.reply_text("❌ Invalid or expired link.")
