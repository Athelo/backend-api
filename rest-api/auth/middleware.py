from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

import firebase_admin
from firebase_admin import auth  # noqa: F401
from flask import Response, request

from utils.socketio_utils import decode_token

a = TypeVar("a")

default_app = firebase_admin.initialize_app()
logger = logging.getLogger()


def jwt_authenticated(func: Callable[..., int]) -> Callable[..., int]:
    """Use the Firebase Admin SDK to parse Authorization header to verify the
    user ID token.

    The server extracts the Identity Platform uid for that user.
    """

    @wraps(func)
    def decorated_function(*args: a, **kwargs: a) -> a:
        header = request.headers.get("Authorization", None)
        if header:
            split_header = header.split(" ")
            if len(split_header) != 2:
                return Response(
                    status=403, response=f"Error with authentication: malformed header."
                )
            token = header.split(" ")[1]
            try:
                decoded_token = firebase_admin.auth.verify_id_token(token)
            except Exception as e:
                logger.exception(e)
                return Response(status=403, response=f"Error with authentication: {e}")
        else:
            return Response(status=401)

        request.uid = decoded_token["uid"]
        request.email = decoded_token["email"]
        return func(*args, **kwargs)

    return decorated_function


def websocket_jwt_authenticated(func: Callable[..., int]) -> Callable[..., int]:
    @wraps(func)
    def decorated_function(*args, **kwargs):
        websocket_token = request.headers.get("WEBSOCKET_TOKEN", None)

        if websocket_token:
            try:
                decoded_token = decode_token(websocket_token)
                request.uid = decoded_token["uid"]
                request.room_id = decoded_token["room_id"]
                request.device_identifier = decoded_token["device_identifier"]
            except Exception as e:
                logger.exception(e)
                return Response(status=403, response=f"Error with websocket authentication: {e}")
        else:
            return Response(status=401)

        return func(*args, **kwargs)

    return decorated_function
