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
        """Add a user if not exists."""
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
            # Update name/username if changed
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"first_name": first_name, "username": username}}
            )

    async def get_user(self, user_id):
        return await self.users.find_one({"user_id": user_id})

    async def get_all_users(self):
        return self.users.find().to_list(length=None)

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

    # ==========================================================
    # 🔹 FILE STORAGE (Single Files & Batches)
    # ==========================================================
    async def save_stored_file(self, unique_id, file_id, message_id, chat_id, owner_id, file_type="single"):
        await self.stored_files.insert_one({
            "unique_id": unique_id,
            "file_id": file_id,
            "message_id": message_id,
            "chat_id": chat_id,
            "owner_id": owner_id,
            "type": file_type,
            "created_at": None
        })

    async def get_stored_file(self, unique_id):
        return await self.stored_files.find_one({"unique_id": unique_id})

    async def delete_stored_file(self, unique_id):
        await self.stored_files.delete_one({"unique_id": unique_id})

    # Batches
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
    # 🔹 BAN / UNBAN
    # ==========================================================
    async def ban_user(self, user_id, reason=None):
        await self.banned_users.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "reason": reason}},
            upsert=True
        )

    async def unban_user(self, user_id):
        await self.banned_users.delete_one({"user_id": user_id})

    async def is_banned(self, user_id):
        record = await self.banned_users.find_one({"user_id": user_id})
        return record is not None

    # ==========================================================
    # 🔹 GLOBAL SETTINGS (Bot-wide)
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


# Global instance
db = Database()
