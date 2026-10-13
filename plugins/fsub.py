# plugins/fsub.py
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageNotModified
from database import db
from utils.fsub_helper import check_subscription, build_fsub_keyboard

fsub_states = {}


async def safe_edit(message, text, markup=None):
    try:
        await message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    except MessageNotModified:
        pass
    except Exception as e:
        print(f"Edit error: {e}")


# ==========================================================
# 🔹 MAIN FORCE SUBSCRIBE MENU
# ==========================================================
@Client.on_callback_query(filters.regex("^main_force_sub$"))
async def fsub_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    status = await db.get_fsub_status(bot_username)
    status_text = "ᴏɴ ✅" if status else "ᴏꜰꜰ ❌"

    text = (
        "📢 **FORCE SUBSCRIBE:**\n\n"
        "ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ:\n"
        "ᴀ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ғᴇᴀᴛᴜʀᴇ ғᴏʀᴄɪɴɢ ᴜsᴇʀs ᴛᴏ sᴜʙsᴄʀɪʙᴇ ᴛᴏ "
        "sᴘᴇᴄɪғɪᴄ ᴄʜᴀɴɴᴇʟs ʙᴇғᴏʀᴇ ᴀᴄᴄᴇssɪɴɢ ᴄᴏɴᴛᴇɴᴛ.\n\n"
        "ɴᴏʀᴍᴀʟ ғsᴜʙ:\n"
        "ʀᴇǫᴜɪʀᴇs ᴛʜᴇ ᴜsᴇʀ ᴛᴏ ᴄʟɪᴄᴋ ᴀ ᴊᴏɪɴ ʙᴜᴛᴛᴏɴ ᴏɴ ᴀ ᴄʜᴀɴɴᴇʟ ᴏʀ "
        "ɢʀᴏᴜᴘ, ᴛʜᴇɴ ʙᴏᴛ ᴄʜᴇᴄᴋs ᴍᴇᴍʙᴇʀsʜɪᴘ ɪɴsᴛᴀɴᴛʟʏ ᴛᴏ ᴜɴʟᴏᴄᴋ "
        "ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ ᴏʀ ᴄʜᴀᴛ ᴀᴄᴄᴇss.\n\n"
        "ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ғsᴜʙ:\n"
        "ʀᴇǫᴜɪʀᴇs ᴛʜᴇ ᴜsᴇʀ ᴛᴏ sᴇɴᴅ ᴀ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ ᴀ ᴘʀɪᴠᴀᴛᴇ "
        "ᴄʜᴀɴɴᴇʟ ᴏʀ ɢʀᴏᴜᴘ ᴛʜᴇɴ ᴜsᴇʀ ᴄᴀɴ ᴀᴄᴄᴇss ᴄᴏɴᴛᴇɴᴛ.\n\n"
        "ʏᴏᴜ ᴄᴀɴ ᴀᴅᴅ ᴍᴜʟᴛɪᴘʟᴇ ᴄʜᴀɴɴᴇʟs\n\n"
        f"ꜰᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ - {status_text}"
    )

    buttons = [
        [InlineKeyboardButton("Add Channel", callback_data="mfsub_add"),
         InlineKeyboardButton("Auto Add Channels", callback_data="mfsub_auto_add")],
        [InlineKeyboardButton("Force Subscribe On/Off", callback_data="mfsub_toggle")],
        [InlineKeyboardButton("Force Subscribe Message", callback_data="mfsub_msg")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_settings")]
    ]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 ADD CHANNEL
# ==========================================================
@Client.on_callback_query(filters.regex("^mfsub_add$"))
async def fsub_add(client: Client, callback_query: CallbackQuery):
    fsub_states[callback_query.from_user.id] = "waiting_fsub_channel"
    text = (
        "❪ **SET CHANNEL** ❫\n\n"
        "ғᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ʏᴏᴜʀ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ "
        "ᴡɪᴛʜ ғᴏʀᴡᴀʀᴅ ᴛᴀɢ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ "
        "ᴡɪᴛʜ ғᴜʟʟ ʀɪɢʜᴛs\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_force_sub")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_message(filters.private, group=90)
async def fsub_receive_channel(client: Client, message: Message):
    user_id = message.from_user.id
    if fsub_states.get(user_id) != "waiting_fsub_channel":
        return
    if message.text and message.text.startswith("/"):
        fsub_states.pop(user_id, None)
        return
    if not message.forward_from_chat:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_force_sub")]]
        return await message.reply_text(
            "⚠️ Forward a message from a channel.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    chat = message.forward_from_chat
    bot_username = (await client.get_me()).username

    try:
        member = await client.get_chat_member(chat.id, "me")
        if member.status not in ("administrator", "creator", "owner"):
            buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_force_sub")]]
            return await message.reply_text(
                f"⚠️ Make @{bot_username} admin in **{chat.title}** first.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_force_sub")]]
        return await message.reply_text(
            f"⚠️ Error: `{e}`",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    fsub_states[user_id] = {
        "state": "waiting_fsub_mode",
        "chat_id": chat.id,
        "chat_name": chat.title
    }

    text = "sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴍᴏᴅᴇ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ғᴏʀ ᴛʜɪs ʙᴇʟᴏᴡ 👇"
    buttons = [
        [InlineKeyboardButton("Normal", callback_data="mfsub_mode_normal"),
         InlineKeyboardButton("Request Channel", callback_data="mfsub_mode_request")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^mfsub_mode_(normal|request)$"))
async def fsub_set_mode(client: Client, callback_query: CallbackQuery):
    mode = callback_query.data.split("_")[-1]
    user_id = callback_query.from_user.id
    state = fsub_states.get(user_id)
    if not isinstance(state, dict) or state.get("state") != "waiting_fsub_mode":
        return await callback_query.answer("Session expired.", show_alert=True)

    bot_username = (await client.get_me()).username
    await db.add_force_channel(bot_username, state["chat_id"], state["chat_name"], mode)
    fsub_states.pop(user_id, None)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_force_sub")]]
    await callback_query.message.edit_text(
        f"✅ **{state['chat_name']}** added as **{mode.title()}** mode.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 TOGGLE ON/OFF
# ==========================================================
@Client.on_callback_query(filters.regex("^mfsub_toggle$"))
async def fsub_toggle(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    current = await db.get_fsub_status(bot_username)
    await db.set_fsub_status(bot_username, not current)
    await callback_query.answer(
        f"Force Sub {'ON ✅' if not current else 'OFF ❌'}",
        show_alert=True
    )
    await fsub_menu(client, callback_query)

# ==========================================================
# 🔹 FORCE SUB MESSAGE MENU
# ==========================================================
@Client.on_callback_query(filters.regex("^mfsub_msg$"))
async def fsub_msg_menu(client: Client, callback_query: CallbackQuery):
    text = (
        "📝 **FORCE SUBSCRIBE MESSAGE:**\n\n"
        "ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴍᴇssᴀɢᴇ: ʏᴏᴜ ᴄᴀɴ ᴄᴜsᴛᴏᴍɪsᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ "
        "ʙᴏᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴍᴇssᴀɢᴇ ᴀɴʏ ᴡᴀʏ ʏᴏᴜ ʟɪᴋᴇ."
    )
    buttons = [
        [InlineKeyboardButton("Set Subscribe Text", callback_data="mfsub_set_text")],
        [InlineKeyboardButton("Set Image", callback_data="mfsub_set_image")],
        [InlineKeyboardButton("Force Channel Button", callback_data="mfsub_set_buttons")],
        [InlineKeyboardButton("🔙 Back", callback_data="main_force_sub")]
    ]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^mfsub_set_text$"))
async def fsub_set_text(client: Client, callback_query: CallbackQuery):
    fsub_states[callback_query.from_user.id] = "waiting_fsub_text"
    text = (
        "sᴇɴᴅ ᴍᴇ ᴀ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴛᴇxᴛ...\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="mfsub_msg")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^mfsub_set_image$"))
async def fsub_set_image(client: Client, callback_query: CallbackQuery):
    fsub_states[callback_query.from_user.id] = "waiting_fsub_image"
    text = (
        "🖼️ sᴇɴᴅ ᴍᴇ ᴀɴ ɪᴍᴀɢᴇ ғᴏʀ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴍᴇssᴀɢᴇ...\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="mfsub_msg")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^mfsub_set_buttons$"))
async def fsub_set_buttons(client: Client, callback_query: CallbackQuery):
    fsub_states[callback_query.from_user.id] = "waiting_fsub_buttons"
    text = (
        "🔘 **Send me buttons in this format:**\n\n"
        "`Button Text - https://link.com`\n\n"
        "One button per line. Multiple lines allowed.\n\n"
        "/cancel - Cancel"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="mfsub_msg")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 RECEIVE TEXT / BUTTONS
# ==========================================================
@Client.on_message(
    filters.private & filters.text & ~filters.command(["cancel", "start"]),
    group=91
)
async def fsub_receive_text(client: Client, message: Message):
    user_id = message.from_user.id
    state = fsub_states.get(user_id)
    bot_username = (await client.get_me()).username

    if state == "waiting_fsub_text":
        await db.set_fsub_text(bot_username, message.text)
        fsub_states.pop(user_id, None)
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="mfsub_msg")]]
        return await message.reply_text(
            "✅ Force Sub text saved.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    if state == "waiting_fsub_buttons":
        lines = message.text.strip().split("\n")
        parsed = []
        for line in lines:
            if " - " in line:
                txt, url = line.split(" - ", 1)
                parsed.append({"text": txt.strip(), "url": url.strip()})
        if not parsed:
            return await message.reply_text(
                "❌ Invalid format. Use: Button Text - https://link.com"
            )
        await db.set_fsub_buttons(bot_username, parsed)
        fsub_states.pop(user_id, None)
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="mfsub_msg")]]
        return await message.reply_text(
            "✅ Buttons saved.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


# ==========================================================
# 🔹 RECEIVE IMAGE
# ==========================================================
@Client.on_message(filters.private & filters.photo, group=92)
async def fsub_receive_image(client: Client, message: Message):
    user_id = message.from_user.id
    if fsub_states.get(user_id) != "waiting_fsub_image":
        return
    bot_username = (await client.get_me()).username
    await db.set_fsub_image(bot_username, message.photo.file_id)
    fsub_states.pop(user_id, None)
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="mfsub_msg")]]
    await message.reply_text(
        "✅ Force Sub image saved.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 AUTO ADD CHANNELS
# ==========================================================
@Client.on_callback_query(filters.regex("^mfsub_auto_add$"))
async def fsub_auto_add(client: Client, callback_query: CallbackQuery):
    fsub_states[callback_query.from_user.id] = "waiting_auto_channels"
    text = (
        "🤖 **AUTO ADD CHANNELS**\n\n"
        "Send me channel IDs (one per line) to add as force-subscribe channels.\n\n"
        "**Format:**\n"
        "`-1001234567890`\n"
        "`-1009876543210`\n\n"
        "Make sure the bot is admin in each channel first.\n\n"
        "/cancel - Cancel this process"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_force_sub")]]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


@Client.on_message(
    filters.private & filters.text & ~filters.command(["cancel", "start"]),
    group=93
)
async def fsub_receive_auto_channels(client: Client, message: Message):
    user_id = message.from_user.id
    if fsub_states.get(user_id) != "waiting_auto_channels":
        return

    bot_username = (await client.get_me()).username
    lines = message.text.strip().split("\n")
    added = []
    failed = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            chat_id = int(line)
            chat = await client.get_chat(chat_id)
            member = await client.get_chat_member(chat_id, "me")
            if member.status not in ("administrator", "creator", "owner"):
                failed.append(f"{chat.title} (not admin)")
                continue
            await db.add_force_channel(bot_username, chat_id, chat.title, "normal")
            added.append(chat.title)
        except Exception as e:
            failed.append(f"{line} ({str(e)[:30]})")

    fsub_states.pop(user_id, None)

    result = "✅ **Auto Add Result**\n\n"
    if added:
        result += f"**Added ({len(added)}):**\n"
        for ch in added:
            result += f"• {ch}\n"
        result += "\n"
    if failed:
        result += f"**Failed ({len(failed)}):**\n"
        for ch in failed:
            result += f"• {ch}\n"

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="main_force_sub")]]
    await message.reply_text(result, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 USER PRESSES "I JOINED" BUTTON
# ==========================================================
@Client.on_callback_query(filters.regex("^fsub_check$"))
async def fsub_check(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    not_joined = await check_subscription(client, callback_query.from_user.id, bot_username)

    if not not_joined:
        await callback_query.answer("✅ Verified!", show_alert=True)
        try:
            await callback_query.message.delete()
        except Exception:
            pass
        await callback_query.message.reply_text(
            "✅ **Verification Complete!**\n\nYou can now send files again."
        )
    else:
        await callback_query.answer(
            "⚠️ You haven't joined all channels yet.",
            show_alert=True
        )
