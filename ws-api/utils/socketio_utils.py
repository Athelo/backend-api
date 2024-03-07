import jwt
from typing import Union
from flask import current_app as app


def generate_token(user_id: Union[str, int], channel_id: Union[str, int], device_identifier: str) -> str:
    """Generate a token to be used for authentication"""
    token = jwt.encode(
        {
            "uid": user_id,
            "channel_id": channel_id,
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
