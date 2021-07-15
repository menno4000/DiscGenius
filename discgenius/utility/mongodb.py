from typing import Callable, List
from fastapi import FastAPI, WebSocket
from fastapi_users.db.mongodb import MongoDBUserDatabase
from motor.motor_asyncio import AsyncIOMotorClient
from .fastapi.user_model import UserDB, UserCreate, UserUpdate, User


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


def get_users_db() -> MongoDBUserDatabase:
    return users_db


async def connect_db():
    """Create database connection."""
    global users_db
    print(f"Connecting to {DATABASE_URL}")
    client = AsyncIOMotorClient(DATABASE_URL, uuidRepresentation="standard")
    db = client[DATABASE_NAME]
    collection = db[USER_DB]
    users_db = MongoDBUserDatabase(UserDB, collection)
    print(f"Connected to {DATABASE_URL}")
    return client


async def close_db():
    """Close database connection."""
    client.close()


def create_start_app_handler(app: FastAPI) -> Callable:  # type: ignore
    async def start_app() -> None:
        await connect_db()

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
    async def stop_app() -> None:
        await close_db()

    return stop_app

# client: AsyncIOMotorClient = None
# client: AsyncIOMotorClient = AsyncIOMotorClient(DATABASE_URL, uuidRepresentation="standard")
# users_db: MongoDBUserDatabase = None
#
#
# def get_db_client() -> motor.motor_asyncio.AsyncIOMotorClient:
#     """Return database client instance."""
#     return client
#
#
# def get_users_db() -> MongoDBUserDatabase:
#     return users_db
#
#
# async def connect_db():
#     """Create database connection."""
#     global users_db
#     print(f"Connecting to {DATABASE_URL}")
#     client = await motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL, uuidRepresentation="standard")
#     db = client["discgenius"]
#     collection = db["users"]
#     users_db = MongoDBUserDatabase(UserDB, collection)
#     print(f"Connected to {DATABASE_URL}")
#     return client
#
#
# async def close_db():
#     """Close database connection."""
#     client.close()
#
#
# SECRET = config['secret']
# SECRET = "95sPvKFS9XtEpsht3NPqZzjDN2Pz3CVz"
#
#
# jwt_authentication = JWTAuthentication(secret=SECRET,
#                                        lifetime_seconds=3600,
#                                        tokenUrl="auth/jwt/login")
#
# db = client["discgenius"]
# user_collection = db["users"]
# user_db = MongoDBUserDatabase(models.BaseUserDB, user_collection)
# fastapi_users = FastAPIUsers(
#     user_db,
#     [jwt_authentication],
#     User,
#     UserCreate,
#     UserUpdate,
#     UserDB,
# )
#
#
# app = FastAPI()
# app.add_event_handler("startup", create_start_app_handler(app=app))
# app.add_event_handler("shutdown", create_stop_app_handler(app=app))
# db = client["discgenius"]
# user_collection = db["users"]
#
# user_db = MongoDBUserDatabase(models.BaseUserDB, user_collection)
# fastapi_users = FastAPIUsers(
#     user_db,
#     [jwt_authentication],
#     User,
#     UserCreate,
#     UserUpdate,
#     UserDB,
# )
#
# app.include_router(
#     fastapi_users.get_auth_router(jwt_authentication),
#     prefix="/auth/jwt",
#     tags=["auth"])
#
# app.include_router(
#     fastapi_users.get_register_router(),
#     prefix="/auth",
#     tags=["auth"],
# )
# # app.include_router(
# #     fastapi_users.get_reset_password_router(
# #         SECRET, after_forgot_password=handlers.on_after_forgot_password
# #     ),
# #     prefix="/auth",
# #     tags=["auth"],
# # )
# # app.include_router(
# #     fastapi_users.get_verify_router(
# #         SECRET, after_verification_request=handlers.after_verification_request
# #     ),
# #     prefix="/auth",
# #     tags=["auth"],
# # )