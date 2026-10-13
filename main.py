from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from database import db
import asyncio

async def main():
    # Initialize Database
    await db.client.admin.command('ping')
    print("Database Connected!")

    # Start Main Bot
    app = Client(
        "MainFileStoreBot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")
    )
    
    await app.start()
    print("Main Bot Started!")
    
    # Keep running
    from pyrogram import idle
    await idle()
    await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
