from http.client import (
    BAD_REQUEST,
    CREATED,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
)
from typing import List
from api.utils import class_route
from repositories.utils import commit_entity
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.message import MessageSchema, MessageCreateSchema
from models.message_channel import MessageChannel
from models.message import Message
from sqlalchemy.exc import NoResultFound
from api.constants import V1_API_PREFIX


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
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = MessageCreateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            abort(UNPROCESSABLE_ENTITY, err.messages)

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
