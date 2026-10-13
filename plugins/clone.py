# plugins/clone.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH
from database import db
import asyncio
import re

# Dictionary to hold running clone clients (in-memory)
active_clones = {}

# 🔹 /clone COMMAND
@Client.on_message(filters.command("clone") & filters.private)
async def clone_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    clone = await db.get_clone(user_id)
    
    if clone:
        buttons = [
            [InlineKeyboardButton(
                f"🤖 @{clone['bot_username']}",
                url=f"https://t.me/{clone['bot_username']}?start=customize"
            )],
            [InlineKeyboardButton("➕ CREATE CLONE", callback_data="create_clone")]
        ]
        await message.reply_text(
            "🛠️ **CLONE MENU**\n\n"
            "WELCOME TO YOUR CLONE BOT MANAGEMENT HUB!\n"
            "CUSTOMIZE YOUR BOT SETTINGS OR MANAGE ITS STATUS.",
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


# 🔹 DETECT TOKEN IN ANY MESSAGE (forwarded or not)
@Client.on_message(filters.private & filters.text & ~filters.command([
    "start", "help", "clone", "link", "batch", "settings", "cancel", "id"
]))
async def receive_token(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text or ""
    
    # Search for token pattern anywhere in the message
    # Pattern: digits : alphanumeric_with_dashes_and_underscores (min 30 chars)
    token_match = re.search(r"(\d{9,11}:[A-Za-z0-9_-]{30,50})", text)
    
    if not token_match:
        return  # Not a token, ignore
    
    token = token_match.group(1)
    
    # 1. Validate token by trying to start a temporary client
    try:
        temp_client = Client(
            f"temp_{user_id}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=token,
            in_memory=True
        )
        await temp_client.start()
        bot_info = await temp_client.get_me()
        await temp_client.stop()
    except Exception as e:
        return await message.reply_text(
            f"❌ **Invalid Token**\n\nError: `{e}`\n\n"
            "Make sure you copied the full token from @BotFather."
        )
    
    # 2. Save to DB
    await db.save_clone_token(user_id, token, bot_info.username)
    
    # 3. Spawn the clone bot in the background
    asyncio.create_task(start_clone_bot(token, user_id, bot_info.username))
    
    await message.reply_text(
        f"✅ **CONGRATULATIONS!**\n\n"
        f"Your @{bot_info.username} bot is successfully created.\n\n"
        f"🔗 Open it: https://t.me/{bot_info.username}\n\n"
        f"Use /clone command to manage it."
    )


# 🔹 CLONE BOT SPAWNER
async def start_clone_bot(token: str, owner_id: int, username: str):
    """Starts a new Pyrogram client for the clone in the background."""
    try:
        clone_app = Client(
            name=f"clone_{owner_id}_{username}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=token,
            plugins=dict(root="clone_plugins"),
            in_memory=True  # No session file needed - critical for Koyeb
        )
        await clone_app.start()
        active_clones[owner_id] = clone_app
        print(f"✅ Clone Bot started: @{username} (Owner: {owner_id})")
    except Exception as e:
        print(f"❌ Failed to start clone @{username}: {e}")
