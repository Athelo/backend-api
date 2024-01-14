import logging
from http.client import (
    BAD_REQUEST,
    CREATED,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
)
from typing import List
from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.message_channel import MessageChannelSchema, MessageChannelRequestSchema
from models.message_channel import MessageChannel
from models.user_profile import UserProfile
from sqlalchemy.exc import IntegrityError, NoResultFound


logger = logging.getLogger()

message_channel_endpoints = Blueprint(
    "Message Channels", __name__, url_prefix="/api/v1/message-channels"
)


def validate_message_channel_request_data() -> dict:
    json_data = request.get_json()
    if not json_data:
        abort(BAD_REQUEST, "No input data provided.")
    schema = MessageChannelRequestSchema()

    try:
        data = schema.load(json_data)
    except ValidationError as err:
        abort(UNPROCESSABLE_ENTITY, err.messages)

    return data


def validate_message_channel_request_participants(data: dict) -> List[UserProfile]:
    user = get_user_from_request(request)
    participants = []
    participants_length = len(data.get("users", None))
    if participants_length < 2:
        abort(
            UNPROCESSABLE_ENTITY,
            f"Message channels require at least two participants, request supplied {participants_length}.",
        )
    for user_id in data["users"]:
        requested_user = db.session.get(UserProfile, user_id)
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


def get_participants_hash(participants: List[UserProfile]) -> int:
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
            .filter(UserProfile.id == user.id)
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
        try:
            db.session.add(channel)
            db.session.commit()
        except IntegrityError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create chat because {e.orig.args[0]['M']}",
            )
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
