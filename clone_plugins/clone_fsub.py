# clone_plugins/clone_fsub.py
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
@Client.on_callback_query(filters.regex("^u_force_sub$"))
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
        [InlineKeyboardButton("Add Channel", callback_data="fsub_add"),
         InlineKeyboardButton("Auto Add Channels", callback_data="fsub_auto_add")],
        [InlineKeyboardButton("Force Subscribe On/Off", callback_data="fsub_toggle")],
        [InlineKeyboardButton("Force Subscribe Message", callback_data="fsub_msg")],
        [InlineKeyboardButton("🔙 Back", callback_data="c_settings")]
    ]
    await safe_edit(callback_query.message, text, InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 ADD CHANNEL
# ==========================================================
@Client.on_callback_query(filters.regex("^fsub_add$"))
async def fsub_add(client: Client, callback_query: CallbackQuery):
    fsub_states[callback_query.from_user.id] = "waiting_fsub_channel"
    text = (
        "❪ **SET CHANNEL** ❫\n\n"
        "ғᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ʏᴏᴜʀ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ᴄʜᴀɴɴᴇʟ "
        "ᴡɪᴛʜ ғᴏʀᴡᴀʀᴅ ᴛᴀɢ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ "
        "ᴡɪᴛʜ ғᴜʟʟ ʀɪɢʜᴛs\n\n"
        "/cancel - ᴄᴀɴᴄᴇʟ ᴛʜɪs ᴘʀᴏᴄᴇss"
    )
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_force_sub")]]
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
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_force_sub")]]
        return await message.reply_text(
            "⚠️ Forward a message from a channel.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    chat = message.forward_from_chat
    bot_username = (await client.get_me()).username

    # Verify bot is admin
    try:
        member = await client.get_chat_member(chat.id, "me")
        if member.status not in ("administrator", "creator", "owner"):
            buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_force_sub")]]
            return await message.reply_text(
                f"⚠️ Make @{bot_username} admin in **{chat.title}** first.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_force_sub")]]
        return await message.reply_text(f"⚠️ Error: `{e}`", reply_markup=InlineKeyboardMarkup(buttons))

    # Store temp state
    fsub_states[user_id] = {
        "state": "waiting_fsub_mode",
        "chat_id": chat.id,
        "chat_name": chat.title
    }

    text = "sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴍᴏᴅᴇ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ғᴏʀ ᴛʜɪs ʙᴇʟᴏᴡ 👇"
    buttons = [
        [InlineKeyboardButton("Normal", callback_data="fsub_mode_normal"),
         InlineKeyboardButton("Request Channel", callback_data="fsub_mode_request")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("^fsub_mode_(normal|request)$"))
async def fsub_set_mode(client: Client, callback_query: CallbackQuery):
    mode = callback_query.data.split("_")[-1]
    user_id = callback_query.from_user.id
    state = fsub_states.get(user_id)
    if not isinstance(state, dict) or state.get("state") != "waiting_fsub_mode":
        return await callback_query.answer("Session expired.", show_alert=True)

    bot_username = (await client.get_me()).username
    await db.add_force_channel(bot_username, state["chat_id"], state["chat_name"], mode)
    fsub_states.pop(user_id, None)

    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="u_force_sub")]]
    await callback_query.message.edit_text(
        f"✅ **{state['chat_name']}** added as **{mode.title()}** mode.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ==========================================================
# 🔹 TOGGLE ON/OFF
# ==========================================================
@Client.on_callback_query(filters.regex("^fsub_toggle$"))
async def fsub_toggle(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    current = await db.get_fsub_status(bot_username)
    await db.set_fsub_status(bot_username, not current)
    await callback_query.answer(
        f"Force Sub {'ON ✅' if not current else 'OFF ❌'}",
        show_alert=True
    )
    await fsub_menu(client, callback_query)
