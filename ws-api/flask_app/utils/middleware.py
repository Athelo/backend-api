import logging

from flask import request, Response
from functools import wraps
from collections.abc import Callable

from flask_app.utils.socketio_utils import decode_token

logger = logging.getLogger()


def websocket_jwt_authenticated(func: Callable[..., int]) -> Callable[..., int]:
    @wraps(func)
    def decorated_function(*args, **kwargs):
        websocket_token = request.headers.get("Websockettoken", None)
        main_token = request.headers.get("Maintoken", None)

        if websocket_token:
            try:
                decoded_token = decode_token(websocket_token)
                request.uid = decoded_token["uid"]
                request.channel_id = decoded_token["channel_id"]
                request.device_identifier = decoded_token["device_identifier"]
                request.main_token = main_token
            except Exception as e:
                logger.exception(e)
                return Response(status=403, response=f"Error with websocket authentication: {e}")
        else:
            return Response(status=401)

        return func(*args, **kwargs)

    return decorated_function
