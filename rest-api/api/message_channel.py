from http.client import (
    CREATED,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
)
from typing import List

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from models.database import db
from models.message_channel import MessageChannel
from models.users import Users
from repositories.utils import commit_entity
from schemas.message_channel import MessageChannelRequestSchema, MessageChannelSchema

from api.utils import class_route, validate_json_body

message_channel_endpoints = Blueprint(
    "Message Channels", __name__, url_prefix="/api/v1/message-channels"
)


def validate_message_channel_request_data() -> dict:
    schema = MessageChannelRequestSchema()
    data = validate_json_body(schema)

    return data


def validate_message_channel_request_participants(data: dict) -> List[Users]:
    user = get_user_from_request(request)
    participants = []
    participants_length = len(data.get("users", None))
    if participants_length < 2:
        abort(
            UNPROCESSABLE_ENTITY,
            f"Message channels require at least two participants, request supplied {participants_length}.",
        )
    for user_id in data["users"]:
        requested_user = db.session.get(Users, user_id)
        participants.append(requested_user)
        if requested_user is None:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create or interact with channel because user {user_id} does not exist.",
            )

    if user not in participants:
        abort(
            UNAUTHORIZED,
            f"Cannot interact with a message channel that doesn't include the current user. Current user {user.id}.",
        )

    return participants


def get_participants_hash(participants: List[Users]) -> int:
    user_ids = [u.id for u in participants]
    user_ids.sort()
    user_set = frozenset(user_ids)
    result = hash(user_set)
    return result


@class_route(message_channel_endpoints, "/", "message_channels")
class MessageChannelsView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        query = (
            db.session.query(MessageChannel)
            .join(MessageChannel.users)
            .filter(Users.id == user.id)
        )

        channel = db.session.scalars(query).all()
        schema = MessageChannelSchema(many=True)
        return schema.dump(channel)

    @jwt_authenticated
    def post(self):
        data = validate_message_channel_request_data()
        participants = validate_message_channel_request_participants(data)
        channel = MessageChannel(
            users=participants,
            users_hash=hash(get_participants_hash(participants)),
        )
        commit_entity(channel)
        result = MessageChannelSchema().dump(channel)
        return result, CREATED


@message_channel_endpoints.route("/search/", methods=["POST"])
@jwt_authenticated
def find_channel_by_members():
    data = validate_message_channel_request_data()
    participants = validate_message_channel_request_participants(data)
    channel = (
        db.session.query(MessageChannel)
        .filter(MessageChannel.users_hash == get_participants_hash(participants))
        .one_or_none()
    )
    return MessageChannelSchema().dump(channel)
