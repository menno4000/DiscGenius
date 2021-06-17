from discgenius.utility.db.database_manager import DatabaseManager
from discgenius.utility.db.mongo_manager import MongoManager

db = MongoManager()


async def get_database() -> DatabaseManager:
    return db
