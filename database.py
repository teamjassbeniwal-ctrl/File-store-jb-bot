import motor.motor_asyncio
from config import DB_URL, DB_NAME

class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
        self.db = self.client[DB_NAME]
        self.users = self.db.users
        self.clones = self.db.clones
        self.files = self.db.files

    # --- User Management ---
    async def add_user(self, user_id):
        if not await self.users.find_one({"user_id": user_id}):
            await self.users.insert_one({"user_id": user_id, "plan": "free"})

    async def get_user(self, user_id):
        return await self.users.find_one({"user_id": user_id})

    # --- Clone Management ---
    async def save_clone_token(self, user_id, token, bot_username):
        await self.clones.update_one(
            {"user_id": user_id},
            {"$set": {"token": token, "bot_username": bot_username}},
            upsert=True
        )

    async def get_clone(self, user_id):
        return await self.clones.find_one({"user_id": user_id})

    # --- File Storage ---
    async def save_file(self, file_id, unique_id, message_id):
        await self.files.insert_one({
            "file_id": file_id,
            "unique_id": unique_id,
            "message_id": message_id
        })

    async def get_file(self, unique_id):
        return await self.files.find_one({"unique_id": unique_id})

db = Database()
