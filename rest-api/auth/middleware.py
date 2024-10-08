from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TypeVar

import firebase_admin
from firebase_admin import auth  # noqa: F401
from flask import Response, redirect, request, session, url_for
from flask import current_app as app

a = TypeVar("a")

default_app = firebase_admin.initialize_app()


def get_token(header) -> str:
    split_header = header.split(" ")
    if len(split_header) != 2:
        return None
    return header.split(" ")[1]


def decode_token(token) -> dict:
    return firebase_admin.auth.verify_id_token(token)


def jwt_authenticated(func: Callable[..., int]) -> Callable[..., int]:
    """Use the Firebase Admin SDK to parse Authorization header to verify the
    user ID token.

    The server extracts the Identity Platform uid for that user.
    """

    @wraps(func)
    def decorated_function(*args: a, **kwargs: a) -> a:
        header = request.headers.get("Authorization", None)
        if header:
            token = get_token(header)
            if token is None:
                return Response(
                    status=403, response="Error with authentication: malformed header."
                )
            try:
                decoded_token = decode_token(token)
            except Exception as e:
                app.logger.exception(e)
                return Response(status=403, response=f"Error with authentication: {e}")
        else:
            return Response(status=401)

        request.uid = decoded_token["uid"]
        request.email = decoded_token["email"]
        return func(*args, **kwargs)

    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get("user")
        print(f"checking login for session: {request.url} {user}")
        if user is None:
            return redirect(url_for("Webapp.render_login"))
        return f(*args, **kwargs)

    return decorated_function
