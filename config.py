# config.py
import os
import sys


# ==========================================================
# 🔹 READ RAW ENVIRONMENT VARIABLES (no hardcoded defaults)
# ==========================================================
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
DB_URL = os.environ.get("DATABASE_URL")
OWNER_ID = os.environ.get("OWNER_ID")


# ==========================================================
# 🔹 VALIDATE REQUIRED VALUES
# ==========================================================
_missing = []
if not API_ID:    _missing.append("API_ID")
if not API_HASH:  _missing.append("API_HASH")
if not BOT_TOKEN: _missing.append("BOT_TOKEN")
if not DB_URL:    _missing.append("DATABASE_URL")
if not OWNER_ID:  _missing.append("OWNER_ID")

if _missing:
    print("❌ Missing required environment variables:")
    for var in _missing:
        print(f"   - {var}")
    print("\nPlease set these in your Koyeb dashboard → Environment Variables.")
    sys.exit(1)


# ==========================================================
# 🔹 SAFE TYPE CONVERSIONS
# ==========================================================
try:
    API_ID = int(API_ID)
except ValueError:
    print(f"❌ API_ID must be an integer, got: {API_ID}")
    sys.exit(1)

try:
    OWNER_ID = int(OWNER_ID)
except ValueError:
    print(f"❌ OWNER_ID must be an integer, got: {OWNER_ID}")
    sys.exit(1)


# ==========================================================
# 🔹 OPTIONAL VALUES (with safe defaults)
# ==========================================================
DB_NAME = os.environ.get("DB_NAME", "FileStoreBot")

try:
    DB_CHANNEL_ID = int(os.environ.get("DB_CHANNEL_ID", "0"))
except ValueError:
    DB_CHANNEL_ID = 0

try:
    FORCE_SUB_CHANNEL = int(os.environ.get("FORCE_SUB_CHANNEL", "0"))
except ValueError:
    FORCE_SUB_CHANNEL = 0


# ==========================================================
# 🔹 STARTUP DEBUG PRINT (safe — no secrets shown)
# ==========================================================
print("✅ Config loaded successfully:")
print(f"   API_ID            : {API_ID}")
print(f"   OWNER_ID          : {OWNER_ID}")
print(f"   DB_NAME           : {DB_NAME}")
print(f"   DB_CHANNEL_ID     : {DB_CHANNEL_ID}")
print(f"   FORCE_SUB_CHANNEL : {FORCE_SUB_CHANNEL}")
# ⚠️ Never print API_HASH, BOT_TOKEN, or DB_URL
