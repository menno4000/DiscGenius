from typing import Callable, List
from fastapi import FastAPI, WebSocket
from fastapi_users.db.mongodb import MongoDBUserDatabase
from motor.motor_asyncio import AsyncIOMotorClient
from .fastapi.user_model import UserDB, UserCreate, UserUpdate, User
import logging

logger = logging.getLogger("utility.mongodb")

DATABASE_URL = "mongodb://127.0.0.1:27017"
DATABASE_NAME = "discgenius"
USER_DB = "users"

client: AsyncIOMotorClient = None
users_db: MongoDBUserDatabase = None


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
