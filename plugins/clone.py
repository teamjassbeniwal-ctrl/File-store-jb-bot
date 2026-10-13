# plugins/clone.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH
from database import db
from utils.logger import log_clone_created
import asyncio
import re

active_clones = {}


# ==========================================================
# 🔹 /clone COMMAND
# ==========================================================
@Client.on_message(filters.command("clone") & filters.private)
async def clone_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    clone = await db.get_clone(user_id)

    if clone:
        text = (
            "🛠️ **CLONE MENU**\n\n"
            "ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʜᴜʙ!\n"
            "ᴄᴜsᴛᴏᴍɪᴢᴇ ʏᴏᴜʀ ʙᴏᴛ sᴇᴛᴛɪɴɢs ᴏʀ ᴍᴀɴᴀɢᴇ ɪᴛs sᴛᴀᴛᴜs.\n\n"
            "⚙️ **QUICK COMMANDS**\n"
            "🚀 /activate — ᴀᴄᴛɪᴠᴀᴛᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ\n"
            "🗑️ /delete — ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ"
        )
        buttons = [
            [InlineKeyboardButton(
                f"🤖 @{clone['bot_username']}",
                url=f"https://t.me/{clone['bot_username']}?start=customize"
            )],
            [InlineKeyboardButton("➕ ADD CLONE", callback_data="create_clone")]
        ]
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(
            "1) SEND /newbot TO @BotFather\n"
            "2) GIVE A NAME FOR YOUR BOT.\n"
            "3) GIVE A UNIQUE USERNAME.\n"
            "4) THEN YOU WILL GET A MESSAGE WITH YOUR BOT TOKEN.\n"
            "5) FORWARD THAT MESSAGE TO ME.\n\n"
            "/cancel - CANCEL THIS PROCESS."
        )


# ==========================================================
# 🔹 RECEIVE TOKEN
# ==========================================================
@Client.on_message(
    filters.private & filters.text &
    ~filters.command(["start", "help", "clone", "link", "batch", "settings", "cancel", "id", "activate", "delete", "broadcast"])
)
async def receive_token(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text or ""

    token_match = re.search(r"(\d{9,11}:[A-Za-z0-9_-]{30,50})", text)
    if not token_match:
        return

    token = token_match.group(1)

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
            f"❌ **Invalid Token**\n\nError: `{e}`"
        )

    await db.save_clone_token(user_id, token, bot_info.username)

    # ==========================================================
    # 🔹 MASTER LOG — Clone Created
    # ==========================================================
    try:
        await log_clone_created(
            client=client,
            owner_id=user_id,
            clone_username=bot_info.username,
            owner_username=message.from_user.username
        )
    except Exception as e:
        print(f"Clone creation log failed: {e}")

    asyncio.create_task(start_clone_bot(token, user_id, bot_info.username))

    await message.reply_text(
        f"✅ **CONGRATULATIONS!**\n\n"
        f"Your @{bot_info.username} bot is successfully created.\n\n"
        f"Use /clone command to manage it."
    )


# ==========================================================
# 🔹 CLONE BOT SPAWNER
# ==========================================================
async def start_clone_bot(token: str, owner_id: int, username: str):
    try:
        clone_app = Client(
            name=f"clone_{owner_id}_{username}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=token,
            plugins=dict(root="clone_plugins"),
            in_memory=True
        )
        await clone_app.start()
        active_clones[owner_id] = clone_app
        print(f"✅ Clone Bot started: @{username} (Owner: {owner_id})")
    except Exception as e:
        print(f"❌ Failed to start clone @{username}: {e}")


# ==========================================================
# 🔹 CREATE CLONE CALLBACK
# ==========================================================
@Client.on_callback_query(filters.regex("create_clone"))
async def create_clone_cb(client: Client, callback_query):
    user_id = callback_query.from_user.id
    clone = await db.get_clone(user_id)

    if clone:
        await callback_query.answer(
            f"⚠️ You already have a clone bot: @{clone['bot_username']}",
            show_alert=True
        )
        return

    await callback_query.message.edit_text(
        "1) SEND /newbot TO @BotFather\n"
        "2) GIVE A NAME FOR YOUR BOT.\n"
        "3) GIVE A UNIQUE USERNAME.\n"
        "4) THEN YOU WILL GET A MESSAGE WITH YOUR BOT TOKEN.\n"
        "5) FORWARD THAT MESSAGE TO ME.\n\n"
        "/cancel - CANCEL THIS PROCESS."
    )


# ==========================================================
# 🔹 /activate COMMAND
# ==========================================================
@Client.on_message(filters.command("activate") & filters.private)
async def activate_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    clone = await db.get_clone(user_id)

    if not clone:
        return await message.reply_text("❌ ɴᴏ ʙᴏᴛ ғᴏᴜɴᴅ ‼️")

    buttons = [
        [InlineKeyboardButton(
            f"🤖 @{clone['bot_username']}",
            url=f"https://t.me/{clone['bot_username']}"
        )],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")]
    ]
    await message.reply_text(
        "🤖 sᴇʟᴇᴄᴛ ᴛʜᴇ ʙᴏᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴄᴛɪᴠᴀᴛᴇ:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 /delete COMMAND
# ==========================================================
@Client.on_message(filters.command("delete") & filters.private)
async def delete_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    clone = await db.get_clone(user_id)

    if not clone:
        return await message.reply_text("❌ ɴᴏ ʙᴏᴛ ғᴏᴜɴᴅ ‼️")

    buttons = [
        [InlineKeyboardButton("🗑️ YES, DELETE", callback_data="confirm_delete")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")]
    ]
    await message.reply_text(
        f"⚠️ **Are you sure?**\n\n"
        f"Deleting @{clone['bot_username']} is permanent and cannot be undone.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 CANCEL ACTION
# ==========================================================
@Client.on_callback_query(filters.regex("cancel_action"))
async def cancel_cb(client: Client, callback_query):
    await callback_query.message.delete()
    await callback_query.answer("Cancelled.")


# ==========================================================
# 🔹 CONFIRM DELETE
# ==========================================================
@Client.on_callback_query(filters.regex("confirm_delete"))
async def confirm_delete_cb(client: Client, callback_query):
    user_id = callback_query.from_user.id
    clone = await db.get_clone(user_id)

    if not clone:
        return await callback_query.answer("No clone found.", show_alert=True)

    if user_id in active_clones:
        try:
            await active_clones[user_id].stop()
            del active_clones[user_id]
        except Exception:
            pass

    await db.clones.delete_one({"user_id": user_id})

    await callback_query.message.edit_text(
        f"✅ **Bot @{clone['bot_username']} has been deleted.**\n\n"
        "You can create a new clone anytime using /clone."
    )
