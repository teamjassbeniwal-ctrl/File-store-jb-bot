from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
import base64

@Client.on_message(filters.command("link") & filters.private)
async def create_link(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to store it.")
    
    # Get the file from the replied message
    file_msg = message.reply_to_message
    file_id = None
    
    if file_msg.document:
        file_id = file_msg.document.file_id
    elif file_msg.video:
        file_id = file_msg.video.file_id
    elif file_msg.photo:
        file_id = file_msg.photo.file_id
    
    if not file_id:
        return await message.reply_text("Unsupported file type.")
    
    # Generate a unique ID
    unique_id = base64.urlsafe_b64encode(str(file_msg.id).encode()).decode()[:10]
    
    # Save to DB
    await db.save_file(file_id, unique_id, file_msg.id)
    
    # Generate Link (You need to replace 'YourMainBot' with your bot username)
    bot_username = (await client.get_me()).username
    link = f"https://t.me/{bot_username}?start={unique_id}"
    
    await message.reply_text(f"✅ **File Stored!**\n\nLink: `{link}`")

@Client.on_message(filters.private & filters.regex(r"^/start (.+)"))
async def retrieve_file(client: Client, message: Message):
    # This catches the deep link
    payload = message.text.split(" ", 1)[1]
    
    if payload == "customize":
        # Handle Customize menu (Image 6)
        from utils.keyboard import clone_settings_kb
        await message.reply_text("Customize your bot:", reply_markup=clone_settings_kb("bot"))
        return

    # Check if payload is a file ID
    file_data = await db.get_file(payload)
    if file_data:
        await message.reply_cached_media(file_data['file_id'], caption="Here is your file.")
    else:
        await message.reply_text("Invalid or expired link.")
