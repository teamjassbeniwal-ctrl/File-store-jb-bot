# clone_plugins/clone_monetization.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import db


# ==========================================================
# 🔹 MONETIZATION MENU (Triggered from Settings)
# ==========================================================
@Client.on_callback_query(filters.regex("^c_monetization$"))
async def monetization_menu(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)
    if not clone_data or clone_data["user_id"] != callback_query.from_user.id:
        return await callback_query.answer("Owner only!", show_alert=True)

    # Check current monetization status from DB
    monetization_on = clone_data.get("monetization", False)
    status_text = "ᴏɴ ✅" if monetization_on else "ᴏғғ ❌"

    text = (
        "💵 **MONETIZATION:**\n\n"
        "💰 **How Bot Monetization Works ?**\n\n"
        "We are introducing a new Monetization Feature for your bot clones! "
        "You can easily turn this feature On or Off anytime from below button.\n\n"
        "**How do you earn money?**\n\n"
        "**The Concept:** You earn money based on how much traffic your bot gets through features like join requests, bot broadcasts, or force subscription channels.\n"
        "**The Rate:** For every 1,000 users that interact with your bot (e.g., daily force join requests on channel), you will earn 100 RS.\n"
        "**Example:** If 1,000 users start your bot today, you make 100 RS today. If 2,000 users start it, you make 200 RS, and so on...\n\n"
        "**When do you get paid?**\n\n"
        "**Weekly Payouts:** Withdrawals will be processed every Sunday.\n\n"
        "For Monetization Related Updates Join : https://t.me/+PKPA7xf5XjM1OWM9\n\n"
        "Currently Monetization Is Available Only In Force Subscribe Means If You Enable Monetization Then Advertisement Channel Came In Your Bot Force Subscribe And From There You Earn.\n\n"
        f"- **ᴄᴜʀʀᴇɴᴛ ᴍᴏᴅᴇ** :- {status_text}"
    )

    toggle_text = "Disable Monetization" if monetization_on else "Enable Monetization"

    buttons = [
        [InlineKeyboardButton("Balance & Withdrawal Info", callback_data="c_monetization_stats")],
        [InlineKeyboardButton(toggle_text, callback_data="c_monetization_toggle")],
        [InlineKeyboardButton("❌ Cancel", callback_data="c_monetization_cancel")]
    ]

    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)


# ==========================================================
# 🔹 MONETIZATION STATS
# ==========================================================
@Client.on_callback_query(filters.regex("^c_monetization_stats$"))
async def monetization_stats(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    bot_id = (await client.get_me()).id
    total_requests = clone_data.get("total_requests", 0) if clone_data else 0
    balance = clone_data.get("balance", 0.00) if clone_data else 0.00

    text = (
        "💰 **Monetization Stats**\n\n"
        f"🤖 **Bot ID:** `{bot_id}`\n"
        f"📊 **Total Requests:** {total_requests}\n"
        f"💵 **Current Balance:** {balance} INR\n\n"
        "⚠️ Illegal tricks not allowed. Fake join requests on channel not allowed.\n"
        "📅 Withdrawal available weekly on Sunday.\n"
        "🤏 Minimum Withdrawal Amount 100 INR.\n"
        "💬 Contact here for withdrawal: @TeamJB_bot"
    )

    buttons = [
        [InlineKeyboardButton("🔙 Back", callback_data="c_monetization")]
    ]

    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ==========================================================
# 🔹 TOGGLE MONETIZATION
# ==========================================================
@Client.on_callback_query(filters.regex("^c_monetization_toggle$"))
async def monetization_toggle(client: Client, callback_query: CallbackQuery):
    bot_username = (await client.get_me()).username
    clone_data = await db.get_clone_by_username(bot_username)

    if not clone_data or clone_data["user_id"] != callback_query.from_user.id:
        return await callback_query.answer("Owner only!", show_alert=True)

    current = clone_data.get("monetization", False)
    new_state = not current

    await db.update_clone_setting(clone_data["user_id"], "monetization", new_state)

    status = "Enabled ✅" if new_state else "Disabled ❌"
    await callback_query.answer(f"Monetization {status}", show_alert=True)
    await monetization_menu(client, callback_query)


# ==========================================================
# 🔹 CANCEL
# ==========================================================
@Client.on_callback_query(filters.regex("^c_monetization_cancel$"))
async def monetization_cancel(client: Client, callback_query: CallbackQuery):
    await callback_query.message.delete()
