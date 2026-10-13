from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
import asyncio
# plugins/clone.py (add at the top)
from config import API_ID, API_HASH

# Dictionary to hold running clone clients
active_clones = {}

@Client.on_message(filters.command("clone") & filters.private)
async def clone_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    clone = await db.get_clone(user_id)
    
    if clone:
        # Image 3: Clone Menu
        buttons = [
            [InlineKeyboardButton(f"🤖 @{clone['bot_username']}", url=f"https://t.me/{clone['bot_username']}?start=customize")],
            [InlineKeyboardButton("➕ CREATE CLONE", callback_data="create_clone")]
        ]
        await message.reply_text(
            "🛠️ **CLONE MENU**\n\nWELCOME TO YOUR CLONE BOT MANAGEMENT HUB!",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        await message.reply_text(
            "1) SEND /newbot TO @BotFather\n"
            "2) GIVE A NAME FOR YOUR BOT.\n"
            "3) GIVE A UNIQUE USERNAME.\n"
            "4) THEN YOU WILL GET A MESSAGE WITH YOUR BOT TOKEN.\n"
            "5) FORWARD THAT MESSAGE TO ME.\n\n"
            "/cancel - CANCEL THIS PROCESS."
        )

@Client.on_message(filters.private & filters.regex(r"^\d{9,10}:[a-zA-Z0-9_-]{35}$"))
async def receive_token(client: Client, message: Message):
    # This regex detects the bot token format
    token = message.text
    user_id = message.from_user.id
    
    # 1. Validate Token
    try:
        temp_client = Client("temp", api_id=API_ID, api_hash=API_HASH, bot_token=token)
        await temp_client.start()
        bot_info = await temp_client.get_me()
        await temp_client.stop()
    except Exception as e:
        return await message.reply_text(f"❌ Invalid Token: {e}")
    
    # 2. Save to DB
    await db.save_clone_token(user_id, token, bot_info.username)
    
    # 3. Spawn the Clone Bot Instance (Runs in background)
    asyncio.create_task(start_clone_bot(token, user_id, bot_info.username))
    
    await message.reply_text(
        f"✅ **CONGRATULATIONS!**\nYour @{bot_info.username} bot is successfully created.\n"
        "You can customize your bot using /clone command."
    )

async def start_clone_bot(token, owner_id, username):
    """Starts a new Pyrogram client for the clone."""
    clone_app = Client(
        name=f"clone_{owner_id}",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=token,
        plugins=dict(root="clone_plugins") # Points to a separate folder for clone logic
    )
    await clone_app.start()
    active_clones[owner_id] = clone_app
    print(f"Started Clone Bot: @{username}")
