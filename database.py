# database.py
import motor.motor_asyncio
from config import DB_URL, DB_NAME


class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
        self.db = self.client[DB_NAME]

        # Collections
        self.users = self.db.users
        self.clones = self.db.clones
        self.stored_files = self.db.stored_files
        self.premium_codes = self.db.premium_codes
        self.banned_users = self.db.banned_users
        self.settings = self.db.settings

    # ==========================================================
    # 🔹 USER MANAGEMENT
    # ==========================================================
    async def add_user(self, user_id, first_name=None, username=None):
        existing = await self.users.find_one({"user_id": user_id})
        if not existing:
            await self.users.insert_one({
                "user_id": user_id,
                "first_name": first_name,
                "username": username,
                "plan": "free",
                "shortlink": False,
                "caption": None,
                "thumbnail": None,
                "auto_delete": 0,
                "protect_content": False,
                "force_sub": False,
                "token_verify": False,
                "joined_at": None
            })
        else:
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"first_name": first_name, "username": username}}
            )

    async def get_user(self, user_id):
        return await self.users.find_one({"user_id": user_id})

    async def get_all_users(self):
        return await self.users.find().to_list(length=None)

    async def update_user_setting(self, user_id, key, value):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {key: value}},
            upsert=True
        )

    async def set_user_plan(self, user_id, plan):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"plan": plan}}
        )

    # ==========================================================
    # 🔹 CLONE BOT MANAGEMENT
    # ==========================================================
    async def save_clone_token(self, user_id, token, bot_username):
        await self.clones.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id,
                "token": token,
                "bot_username": bot_username,
                "active": True,
                "monetization": False,
                "start_text": None,
                "start_pic": None,
                "start_buttons": [],
                "log_channel": None,
                "db_channel": None,
                "admins": [],
                "bot_mode": "public",
                "total_requests": 0,
                "balance": 0.00
            }},
            upsert=True
        )

    async def get_clone(self, user_id):
        return await self.clones.find_one({"user_id": user_id})

    async def get_clone_by_username(self, bot_username):
        return await self.clones.find_one({"bot_username": bot_username})

    async def get_all_clones(self):
        return await self.clones.find().to_list(length=None)

    async def update_clone_setting(self, user_id, key, value):
        await self.clones.update_one(
            {"user_id": user_id},
            {"$set": {key: value}}
        )

    async def delete_clone(self, user_id):
        await self.clones.delete_one({"user_id": user_id})

    async def set_clone_active(self, user_id, active: bool):
        await self.clones.update_one(
            {"user_id": user_id},
            {"$set": {"active": active}}
        )

    async def increment_balance(self, user_id, amount):
        await self.clones.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount, "total_requests": 1}}
        )

    # ==========================================================
    # 🔹 FILE STORAGE (Single & Batches)
    # ==========================================================
    async def save_stored_file(self, unique_id, file_id, message_id, chat_id, owner_id, file_type="single"):
        await self.stored_files.insert_one({
            "unique_id": unique_id,
            "file_id": file_id,
            "message_id": message_id,
            "chat_id": chat_id,
            "owner_id": owner_id,
            "type": file_type
        })

    async def get_stored_file(self, unique_id):
        return await self.stored_files.find_one({"unique_id": unique_id})

    async def delete_stored_file(self, unique_id):
        await self.stored_files.delete_one({"unique_id": unique_id})

    async def save_batch(self, unique_id, from_chat_id, start_id, count, owner_id):
        await self.stored_files.insert_one({
            "unique_id": unique_id,
            "from_chat_id": from_chat_id,
            "start_id": start_id,
            "count": count,
            "owner_id": owner_id,
            "type": "batch"
        })

    async def get_batch(self, unique_id):
        return await self.stored_files.find_one({"unique_id": unique_id, "type": "batch"})

    # ==========================================================
    # 🔹 PREMIUM CODES
    # ==========================================================
    async def create_premium_code(self, code, duration_days, created_by):
        await self.premium_codes.insert_one({
            "code": code,
            "duration_days": duration_days,
            "created_by": created_by,
            "used": False,
            "used_by": None
        })

    async def redeem_premium_code(self, code, user_id):
        record = await self.premium_codes.find_one({"code": code, "used": False})
        if not record:
            return None
        await self.premium_codes.update_one(
            {"code": code},
            {"$set": {"used": True, "used_by": user_id}}
        )
        return record

    # ==========================================================
    # 🔹 PREMIUM PLAN TEXT
    # ==========================================================
    async def set_premium_plan_text(self, bot_username, text):
        await self.settings.update_one(
            {"key": f"premium_text_{bot_username}"},
            {"$set": {"key": f"premium_text_{bot_username}", "value": text}},
            upsert=True
        )

    async def get_premium_plan_text(self, bot_username):
        record = await self.settings.find_one({"key": f"premium_text_{bot_username}"})
        return record["value"] if record else None

    async def delete_premium_plan_text(self, bot_username):
        await self.settings.delete_one({"key": f"premium_text_{bot_username}"})

    # ==========================================================
    # 🔹 PREMIUM USERS
    # ==========================================================
    async def add_premium_user(self, user_id, bot_username):
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {f"premium_{bot_username}": True}}
        )

    async def remove_premium_user(self, user_id, bot_username):
        await self.users.update_one(
            {"user_id": user_id},
            {"$unset": {f"premium_{bot_username}": ""}}
        )

    async def is_premium_user(self, user_id, bot_username):
        user = await self.users.find_one({"user_id": user_id})
        if user:
            return user.get(f"premium_{bot_username}", False)
        return False

    async def get_premium_users_list(self, bot_username):
        cursor = self.users.find({f"premium_{bot_username}": True})
        return await cursor.to_list(length=None)

    async def set_premium_mode(self, bot_username, enabled: bool):
        await self.settings.update_one(
            {"key": f"premium_mode_{bot_username}"},
            {"$set": {"key": f"premium_mode_{bot_username}", "value": enabled}},
            upsert=True
        )

    async def get_premium_mode(self, bot_username):
        record = await self.settings.find_one({"key": f"premium_mode_{bot_username}"})
        return record["value"] if record else False

#
    # ==========================================================
    # BAN / UNBAN
    # ==========================================================

    async def ban_user(self, user_id, reason=None):
        await self.banned_users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "reason": reason
                }
            },
            upsert=True
        )

    async def unban_user(self, user_id):
        await self.banned_users.delete_one(
            {"user_id": user_id}
        )

    async def is_banned(self, user_id):
        record = await self.banned_users.find_one(
            {"user_id": user_id}
        )
        return record is not None

    # ==========================================================
    # GLOBAL SETTINGS
    # ==========================================================

    async def get_setting(self, key, default=None):
        record = await self.settings.find_one({"key": key})
        if record:
            return record.get("value", default)
        return default

    async def set_setting(self, key, value):
        await self.settings.update_one(
            {"key": key},
            {"$set": {"key": key, "value": value}},
            upsert=True
        )

    async def delete_setting(self, key):
        await self.settings.delete_one({"key": key})

    # ==========================================================
    # LOG CHANNEL
    # ==========================================================

    async def set_log_channel(self, bot_username, channel_id):
        key = f"log_channel_{bot_username}"
        await self.settings.update_one(
            {"key": key},
            {"$set": {"key": key, "value": channel_id}},
            upsert=True
        )

    async def get_log_channel(self, bot_username):
        record = await self.settings.find_one(
            {"key": f"log_channel_{bot_username}"}
        )
        return record.get("value") if record else None

    async def delete_log_channel(self, bot_username):
        await self.settings.delete_one(
            {"key": f"log_channel_{bot_username}"}
        )

    # ==========================================================
    # DATABASE CHANNEL
    # ==========================================================

    async def set_db_channel(self, bot_username, channel_id):
        key = f"db_channel_{bot_username}"
        await self.settings.update_one(
            {"key": key},
            {"$set": {"key": key, "value": channel_id}},
            upsert=True
        )

    async def get_db_channel(self, bot_username):
        record = await self.settings.find_one(
            {"key": f"db_channel_{bot_username}"}
        )
        return record.get("value") if record else None

    async def delete_db_channel(self, bot_username):
        await self.settings.delete_one(
            {"key": f"db_channel_{bot_username}"}
        )

    # ==========================================================
    # CLONE ADMIN MANAGEMENT
    # ==========================================================

    async def add_clone_admin(self, bot_username, user_id):
        await self.clones.update_one(
            {"bot_username": bot_username},
            {"$addToSet": {"admins": user_id}}
        )

    async def remove_clone_admin(self, bot_username, user_id):
        await self.clones.update_one(
            {"bot_username": bot_username},
            {"$pull": {"admins": user_id}}
        )

    async def get_clone_admins(self, bot_username):
        clone = await self.clones.find_one(
            {"bot_username": bot_username}
        )
        return clone.get("admins", []) if clone else []

    async def is_clone_admin(self, bot_username, user_id):
        clone = await self.clones.find_one(
            {"bot_username": bot_username}
        )
        if not clone:
            return False
        return user_id in clone.get("admins", [])

    # ==========================================================
    # START MESSAGE CUSTOMIZATION
    # ==========================================================

    async def set_start_text(self, bot_username, text):
        await self.update_clone_by_username(
            bot_username, "start_text", text
        )

    async def set_start_pic(self, bot_username, file_id):
        await self.update_clone_by_username(
            bot_username, "start_pic", file_id
        )

    async def set_start_buttons(self, bot_username, buttons):
        await self.update_clone_by_username(
            bot_username, "start_buttons", buttons
        )

    async def update_clone_by_username(
        self, bot_username, key, value
    ):
        await self.clones.update_one(
            {"bot_username": bot_username},
            {"$set": {key: value}}
        )

    # ==========================================================
    # BOT MODE
    # ==========================================================

    async def set_bot_mode(self, bot_username, mode):
        await self.update_clone_by_username(
            bot_username, "bot_mode", mode
        )

    async def get_bot_mode(self, bot_username):
        clone = await self.clones.find_one(
            {"bot_username": bot_username}
        )
        return clone.get("bot_mode", "public") if clone else "public"

    # ==========================================================
    # MONETIZATION
    # ==========================================================

    async def set_monetization(self, bot_username, enabled: bool):
        await self.update_clone_by_username(
            bot_username, "monetization", enabled
        )

    async def get_monetization(self, bot_username):
        clone = await self.clones.find_one(
            {"bot_username": bot_username}
        )
        return clone.get("monetization", False) if clone else False

    async def get_monetization_stats(self, bot_username):
        clone = await self.clones.find_one(
            {"bot_username": bot_username}
        )
        if not clone:
            return {
                "total_requests": 0,
                "balance": 0.00
            }

        return {
            "total_requests": clone.get("total_requests", 0),
            "balance": clone.get("balance", 0.00)
        }

    # ==========================================================
    # CLEANUP / UTILITIES
    # ==========================================================

    async def delete_all_user_data(self, user_id):
        await self.users.delete_one({"user_id": user_id})
        await self.clones.delete_one({"user_id": user_id})
        await self.banned_users.delete_one({"user_id": user_id})

    async def count_users(self):
        return await self.users.count_documents({})

    async def count_clones(self):
        return await self.clones.count_documents({})

    async def count_files(self):
        return await self.stored_files.count_documents({})

    async def get_bot_stats(self):
        return {
            "total_users": await self.count_users(),
            "total_clones": await self.count_clones(),
            "total_files": await self.count_files(),
            "banned_users": await self.banned_users.count_documents({})
        }


# Global database instance
db = Database()
