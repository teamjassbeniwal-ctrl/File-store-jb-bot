# clone_plugins/clone_files.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from utils.shortener import shorten_url
from utils.verify_helper import needs_verification, mark_verified
from utils.fsub_helper import check_subscription, build_fsub_keyboard
from utils.fsub_middleware import check_force_sub
import base64
import time

user_states = {}


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
        "𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗧𝗵𝗲 𝗙𝗶𝗿𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 𝗙𝗿𝗼𝗺 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 "
        "(𝗪𝗶𝘁𝗵 𝗙𝗼𝗿𝘄𝗮𝗿𝗱 𝗧𝗮𝗴).. 𝗢𝗿 𝗚𝗶𝘃𝗲 𝗠𝗲 𝗙𝗶𝗿𝘀𝘁 𝗠𝗲𝘀𝘀𝗮𝗴𝗲 "
        "𝗟𝗶𝗻𝗸 𝗙𝗿𝗼𝗺 𝗬𝗼𝘂𝗿 𝗕𝗮𝘁𝗰𝗵 𝗖𝗵𝗮𝗻𝗻𝗲𝗹\n\n"
        f"ɴᴏᴛᴇ : ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜɪs @{bot_username}  ʙᴏᴛ ɪs ᴀᴅᴍɪɴ "
        "ɪɴ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜ ғᴜʟʟ ʀɪɢʜᴛ",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 /custom_batch
# ==========================================================
@Client.on_message(filters.command("custom_batch") & filters.private)
async def clone_custom_batch(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return

    user_states[message.from_user.id] = "waiting_for_custom_batch"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(
        "📝 **CUSTOM BATCH**\n\nSend message links (one per line).",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 /multiple_batch
# ==========================================================
@Client.on_message(filters.command("multiple_batch") & filters.private)
async def clone_multiple_batch(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return

    user_states[message.from_user.id] = "waiting_for_multiple_batch"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(
        "📦 **MULTIPLE BATCH**\n\nSend multiple channel messages (one per line).",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 /special_link
# ==========================================================
@Client.on_message(filters.command("special_link") & filters.private)
async def clone_special_link(client: Client, message: Message):
    bot_username = (await client.get_me()).username
    if not await check_force_sub(client, message, bot_username):
        return

    user_states[message.from_user.id] = "waiting_for_special_link"
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="c_back")]]
    await message.reply_text(
        "✨ **SPECIAL LINK**\n\nSend me the file to store with custom settings.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ==========================================================
# 🔹 HANDLE SINGLE FILE FOR /link
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

            default_text = (
                "📢 **Please Join Our Channels**\n\n"
                "To use this bot, you must join the channels below.\n"
                "After joining, click **✅ I Joined**."
            )
            msg_text = fsub_text or default_text

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
            f"ʜᴇʏ {message.from_user.first_name}\n\n"
            "ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴅᴀʏ 😐\n"
            "ᴛᴀᴘ ᴏɴ ᴛʜᴇ ᴠᴇʀɪғʏ ʟɪɴᴋ & ɢᴇᴛ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss "
            "ꜰᴏʀ ᴛɪʟʟ ɴᴇxᴛ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ 😊.\n\n"
            "#ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ:- 1/2",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

    # File processing
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

    buttons = [
        [InlineKeyboardButton("🔗 Open Link", url=final_link)],
        [InlineKeyboardButton("🔙 Back", callback_data="c_back")]
    ]
    await message.reply_text(
        f"✅ **File Stored Successfully!**\n\n🔗 **Link:**\n`{final_link}`",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
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

            default_text = (
                "📢 **Please Join Our Channels**\n\n"
                "To use this bot, you must join the channels below.\n"
                "After joining, click **✅ I Joined**."
            )
            msg_text = fsub_text or default_text

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
            f"ʜᴇʏ {message.from_user.first_name}\n\n"
            "ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴅᴀʏ 😐\n"
            "#ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ:- 1/2",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

    # Batch processing
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
    await message.reply_text(
        "✅ **Verification Complete!**\n\nNow you can download files."
    )


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
