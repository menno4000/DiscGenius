from fastapi import Request
from .user_model import UserDB
import logging

logger = logging.getLogger("utility.fastapi.handlers")

def on_after_register(user: UserDB, request: Request):
    logger.info(f"User {user.id} has registered.")


def on_after_forgot_password(user: UserDB, token: str, request: Request):
    logger.info(f"User {user.id} has forgot their password. Reset token: {token}")


def after_verification_request(user: UserDB, token: str, request: Request):
    logger.info(f"Verification requested for user {user.id}. Verification token: {token}")
