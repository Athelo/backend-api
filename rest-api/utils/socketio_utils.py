import jwt
import random
import string

from flask import current_app as app


def generate_room_code(length: int = 16, existing_rooms: list[str] = None) -> str:
    """Generate a random room code of length 'length' that is not in the list of existing rooms"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if code not in (existing_rooms or []):
            return code


def generate_token(user_id: str, room_code: str, device_identifier: str) -> str:
    """Generate a token to be used for authentication"""
    token = jwt.encode(
        {
            "uid": user_id,
            "room_id": room_code,
            "device_identifier": device_identifier
        },
        app.config.get("WEBSOCKET_JWT_SECRET_KEY"),
        algorithm=app.config.get("WEBSOCKET_JWT_ALGORITHM"),
    )
    return token


def decode_token(token: str) -> dict:
    """Decode a token"""
    try:
        decoded_token = jwt.decode(
            token,
            app.config.get("WEBSOCKET_JWT_SECRET_KEY"),
            algorithms=[app.config.get("WEBSOCKET_JWT_ALGORITHM")],
        )
        return decoded_token
    except jwt.exceptions.PyJWTError:
        raise Exception("Invalid websocket token")
