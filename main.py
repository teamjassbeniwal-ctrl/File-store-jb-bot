# main.py
import sys
import os
import asyncio

# Force Python to look in the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
from database import db

# aiohttp for the Koyeb health check server
from aiohttp import web


# 🔹 HEALTH CHECK SERVER (for Koyeb)
async def health_check(request):
    return web.Response(text="Bot is alive!", status=200)


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    runner = web.AppRunner(app)
    await runner.setup()

    # Koyeb requires binding to 0.0.0.0 on the specified port
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"✅ Health check server running on port {port}")


# 🔹 MAIN BOT
async def main():
    # 1. Connect Database
    await db.client.admin.command("ping")
    print("✅ Database Connected!")

    # 2. Start Health Check Web Server (runs in background)
    asyncio.create_task(start_web_server())

    # 3. Start Main Telegram Bot
    app = Client(
        "MainFileStoreBot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        plugins=dict(root="plugins")
    )

    await app.start()
    print("✅ Main Bot Started!")

    # Keep running forever
    await idle()
    await app.stop()


if __name__ == "__main__":
    asyncio.run(main())
