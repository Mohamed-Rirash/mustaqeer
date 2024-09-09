from datetime import datetime, timedelta
import logging
from typing import Annotated
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
import base64
import jwt
from sqlalchemy import bindparam, select
from sqlalchemy.orm import joinedload

from app.config import settings
from app.models.users import UserToken
from fastapi.security import OAuth2PasswordBearer
from app.models.users import User
from app.config.dependencies import db_dependency

SPECIAL_CHARACTERS = ["@", "#", "$", "%", "=", ":", "?", ".", "/", "|", "~", ">"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
from app.config.settings import settings


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def is_password_strong_enough(password: str) -> bool:
    """
    Checks if a password is strong enough.

    A password is considered strong enough if it has a length of at least 8
    characters, contains at least one uppercase letter, one lowercase letter,
    one digit, and one special character.

    :param password: The password to check.
    :return: True if the password is strong enough, False otherwise.
    """
    conditions = [
        lambda s: len(s) >= 8,
        lambda s: any(c.isupper() for c in s),
        lambda s: any(c.islower() for c in s),
        lambda s: any(c.isdigit() for c in s),
        lambda s: any(c in SPECIAL_CHARACTERS for c in s),
    ]

    return all(condition(password) for condition in conditions)


def str_encode(string: str) -> str:
    return base64.b85encode(string.encode("ascii")).decode("ascii")



def generate_token(payload: dict, secret_key: str, algorithm: str, expire: timedelta) -> str:
    expire_datetime = datetime.utcnow() + expire
    payload.update({"exp": expire_datetime})
    return jwt.encode(payload, secret_key, algorithm=algorithm)


async def load_user(email: str, db):

    try:
        query = select(User).where(User.email == bindparam("email"))
        user = await db.execute(
            query,
            {"email": email},
        )
        user = user.scalars().first()
        print(f"user: {user}")
    except Exception as user_exec:
        logging.info(f"User Not Found, Email: {email}")
        user = None
    return user

# they for using jwt in fastapi

def str_decode(string: str) -> str:
    return base64.b85decode(string.encode("ascii")).decode("ascii")



import logging

def verify_token(token: str, secret: str, algo: str):
    """
    Verify and decode the JWT token using the specified secret and algorithm.

    Args:
        token (str): The JWT token to verify.
        secret (str): The secret key used to decode the JWT.
        algo (str): The algorithm used to decode the JWT (e.g., 'HS256').

    Returns:
        dict: The decoded payload if the token is valid, otherwise None.
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(token, secret, algorithms=[algo])
        logging.debug(f"Decoded payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        logging.warning("JWT token has expired.")
        return None
    except jwt.InvalidTokenError as e:
        logging.warning(f"Invalid JWT token: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error decoding JWT token: {str(e)}")
        return None



async def get_token_user(token: str, db) -> dict:
    payload = verify_token(token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    if payload:
        user_token_id = str_decode(payload.get("r"))
        user_id = str_decode(payload.get("sub"))
        access_key = payload.get("a")
        if user_token_id and user_id and access_key:
            user = await db.execute(
                select(UserToken)
                .options(joinedload(UserToken.user))
                .filter(
                    UserToken.access_token == access_key,
                    UserToken.id == user_token_id,
                    UserToken.user_id == user_id,
                    UserToken.expires_at > datetime.utcnow(),
                )
            )
            user_token = user.scalars().first()
            logging.debug(f"User Token: {user_token}")
            if user_token:
                return user_token.user
    return None

async def get_current_user(db: db_dependency, token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    user = await get_token_user(token, db)
    if user:
        return user
    raise HTTPException(status_code=401, detail="Not authorised.")


user_dependency = Annotated[dict, Depends(get_current_user)]




def get_token_payload(token: str, secret: str, algo: str):
    try:
        payload = jwt.decode(token, secret, algorithms=algo)
    except Exception as jwt_exec:
        logging.debug(f"JWT Error: {str(jwt_exec)}")
        payload = None
    return payload
