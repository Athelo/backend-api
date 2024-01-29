import logging
from http.client import BAD_REQUEST

import firebase_admin
from firebase_admin import auth
from flask import Blueprint, request, jsonify, abort

from models import Users, MessageChannel
from models.database import db
from utils.flask_request_utils import get_request_json_dict_or_raise_exception

logger = logging.getLogger()
socket_endpoints = Blueprint("Socket Connection", __name__, url_prefix="/api/v1/chats/")


@socket_endpoints.post("/sign-in")
def sign_in():
    """
    User sign in
    """
    request_body = get_request_json_dict_or_raise_exception(request)
    token = request_body.get("token")

    try:
        decoded_token = firebase_admin.auth.verify_id_token(token)
    except Exception as e:
        logger.exception(e)
        abort(BAD_REQUEST, f"Error with authentication: {e}")

    email = decoded_token["email"]

    user = db.session.query(Users).filter_by(email=email).one()
    channels = db.session.query(MessageChannel).filter(MessageChannel.users.contains(user)).all()

    dict_channels = []
    for channel in channels:
        dict_channels.append({
            'id': channel.id,
            'name': ', '.join([user.display_name for user in channel.users])
        })

    return jsonify({
        "id": user.id,
        "name": user.display_name,
        "is_admin": user.is_admin,
        "message_channels": dict_channels
    })
