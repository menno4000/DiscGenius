import logging
from typing import List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .database_manager import DatabaseManager
from ..fastapi.user_model import UserDB


class MongoManager(DatabaseManager):
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    async def connect_to_database(self, path: str):
        logging.info("Connecting to MongoDB.")
        self.client = AsyncIOMotorClient(
            path,
            maxPoolSize=10,
            minPoolSize=10)
        self.db = self.client.main_db
        logging.info("Connected to MongoDB.")

    async def close_database_connection(self):
        logging.info("Closing connection with MongoDB.")
        self.client.close()
        logging.info("Closed connection with MongoDB.")

    async def get_posts(self) -> List[UserDB]:
        posts_list = []
        posts_q = self.db.posts.find()
        async for post in posts_q:
            posts_list.append(UserDB(**post, id=post['_id']))
        return posts_list

    async def get_post(self, post_id: str) -> UserDB:
        post_q = await self.db.posts.find_one({'_id': ObjectId(post_id)})
        if post_q:
            return UserDB(**post_q, id=post_q['_id'])

    async def delete_post(self, post_id: str):
        await self.db.posts.delete_one({'_id': ObjectId(post_id)})

    async def update_post(self, post_id: str, post: UserDB):
        await self.db.posts.update_one({'_id': ObjectId(post_id)},
                                       {'$set': post.dict(exclude={'id'})})

    async def add_post(self, post: UserDB):
        await self.db.posts.insert_one(post.dict(exclude={'id'}))
