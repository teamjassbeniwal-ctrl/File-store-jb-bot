from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from utils.keyboard import main_settings_kb

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    await db.add_user(user_id)
    
    # Check if user has a clone
    clone = await db.get_clone(user_id)
    
    if clone:
        # Image 2: User has clone, show full menu
        await message.reply_text(
            "**HERE IS THE SETTINGS MENU**\n\nCUSTOMIZE YOUR SETTINGS AS PER YOUR NEED",
            reply_markup=main_settings_kb(user_id)
        )
    else:
        # Image 1: User does not have a clone
        buttons = [
            [InlineKeyboardButton("➕ CREATE OWN CLONE", callback_data="create_clone")],
            [InlineKeyboardButton("🔍 HELP", callback_data="help")],
            [InlineKeyboardButton("🔍 ABOUT", callback_data="about")]
        ]
        await message.reply_text(
            "**HEY 👋,**\n\nI AM A PERMANENT FILE STORE BOT WITH CLONE AND MANY AMAZING ADVANCE FEATURES.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    # This matches your text block
    help_text = """
🎓 **HELP MENU:**

🤖 ɪ ᴀᴍ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ
📨 ᴍʏ ɴᴀᴍᴇ ɪꜱ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ...

📚 **BASIC COMMANDS**
➤ /start - ᴄʜᴇᴄᴋ ɪꜰ ɪ'ᴍ ᴀʟɪᴠᴇ.
➤ /id - ɢᴇᴛ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ.

📦 **FILE STORAGE COMMANDS**
➤ /link - ꜱᴛᴏʀᴇ ᴀ ꜱɪɴɢʟᴇ ꜰɪʟᴇ ᴏʀ ᴍᴇꜱꜱᴀɢᴇ.
➤ /batch - ꜱᴛᴏʀᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴄᴏɴꜱᴇᴄᴜᴛɪᴠᴇ ᴍᴇꜱꜱᴀɢᴇꜱ.

🤖 **CLONE BOT COMMANDS**
➤ /clone - ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴄʟᴏɴᴇ ʙᴏᴛ.
➤ /activate - ᴀᴄᴛɪᴠᴀᴛᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ.
➤ /delete - ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ.
    """
    await message.reply_text(help_text)
