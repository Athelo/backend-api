from __future__ import annotations

import logging
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

import firebase_admin
from firebase_admin import auth  # noqa: F401
from flask import Response, request

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
        # import pdb

        # pdb.set_trace()
        header = request.headers.get("Authorization", None)
        logger.critical(header)
        if header:
            token = header.split(" ")[1]
            try:
                decoded_token = firebase_admin.auth.verify_id_token(token)
                logger.critical(decoded_token)
            except Exception as e:
                logger.exception(e)
                return Response(status=403, response=f"Error with authentication: {e}")
        else:
            return Response(status=401)

        request.uid = decoded_token["uid"]
        return func(*args, **kwargs)

    return decorated_function
