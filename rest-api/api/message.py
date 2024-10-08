from http.client import (
    BAD_REQUEST,
    CREATED,
    UNAUTHORIZED,
)
from typing import List

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from models.database import db
from models.message import Message
from models.message_channel import MessageChannel
from repositories.utils import commit_entity
from schemas.message import MessageCreateSchema, MessageSchema
from sqlalchemy.exc import NoResultFound

from api.constants import V1_API_PREFIX
from api.utils import class_route, validate_json_body

message_endpoints = Blueprint(
    "Messages", __name__, url_prefix=f"{V1_API_PREFIX}/message-channels"
)


@class_route(message_endpoints, "/<int:message_channel_id>/messages/", "messages")
class MessagesView(MethodView):
    @jwt_authenticated
    def get(self, message_channel_id):
        user = get_user_from_request(request)
        channel = db.session.get(MessageChannel, message_channel_id)
        if channel is None:
            abort(
                BAD_REQUEST,
                f"Cannot add message to channel id {message_channel_id} because it does not exist or the current user is not a part of it.",
            )

        if user not in channel.users:
            return (
                f"Cannot add message to channel id {message_channel_id} because it does not exist or the current user is not a part of it.",
                UNAUTHORIZED,
            )

        schema = MessageSchema(many=True)
        return schema.dump(channel.messages)

    @jwt_authenticated
    def post(self, message_channel_id):
        user = get_user_from_request(request)
        schema = MessageCreateSchema()
        data = validate_json_body(schema)

        try:
            channel = db.session.get(MessageChannel, message_channel_id)
        except NoResultFound:
            abort(
                BAD_REQUEST,
                f"Cannot add message to channel id {channel.id} because it does not exist.",
            )

        message = Message(author_id=user.id, content=data["content"], channel=channel)
        commit_entity(message)

        result = MessageSchema().dump(message)
        return result, CREATED

    def get_participants_hash(self, participants: List[int]) -> int:
        user_ids = [u.id for u in participants]
        user_ids.sort()
        user_set = frozenset(user_ids)
        return hash(user_set)
