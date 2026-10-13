import os

# Get these from my.telegram.org
API_ID = int(os.environ.get("API_ID", "25331263"))
API_HASH = os.environ.get("API_HASH", "cab85305bf85125a2ac053210bcd1030")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_main_bot_token_here")

# Your MongoDB URL (from MongoDB Atlas)
DB_URL = os.environ.get("DATABASE_URL", "mongodb+srv://teamjassbeniwal_db_user:jassbeniwal2005@cluster0.pfxdcwy.mongodb.net/botdb?retryWrites=true&w=majority")
DB_NAME = "FileStoreBot"

# Your Telegram ID (Owner)
OWNER_ID = int(os.environ.get("OWNER_ID", "1955406483"))
DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", 0))
# Force Subscribe Channel ID (e.g., -100123456789)
FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", 0))
