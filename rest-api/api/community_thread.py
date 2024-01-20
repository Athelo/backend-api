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
from schemas.community_thread import CommunityThreadSchema, CommunityThreadListSchema
from models.community_thread import CommunityThread
from models.user_profile import UserProfile
from sqlalchemy.exc import IntegrityError, NoResultFound
from api.constants import V1_API_PREFIX


logger = logging.getLogger()

message_channel_endpoints = Blueprint(
    "Community Threads", __name__, url_prefix=f"{V1_API_PREFIX}/community-threads"
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


@class_route(message_channel_endpoints, "/", "")
class CommunityThreadView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        community_threads = (
            db.session.query(CommunityThread).join(CommunityThread.users).all()
        )
        joined = [thread for thread in community_threads if user in thread.participants]
        not_joined = set(community_threads) - set(joined)
        schema = CommunityThreadListSchema()
        return schema.dump(
            {"joined_community_threads": joined, "other_community_threads": not_joined}
        )

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
