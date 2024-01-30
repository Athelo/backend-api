from http.client import BAD_REQUEST, UNPROCESSABLE_ENTITY, UNAUTHORIZED
from typing import List

from flask import abort
from marshmallow import ValidationError

from auth.utils import get_user_from_request
from cache import cache
from models import MessageChannel, Users
from models.database import db
from schemas.message_channel import MessageChannelDetailResponseSchema, MessageDetailSchema, MemberDetailSchema, \
    MessageChannelRequestSchema
from utils.socketio_utils import generate_token


def validate_message_channel_request_data(request) -> dict:
    json_data = request.get_json()
    if not json_data:
        abort(BAD_REQUEST, "No input data provided.")
    schema = MessageChannelRequestSchema()

    try:
        data = schema.load(json_data)
    except ValidationError as err:
        abort(UNPROCESSABLE_ENTITY, err.messages)

    return data


def validate_message_channel_request_participants(request, data: dict) -> List[Users]:
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


def get_message_channels_for_user(user: Users) -> List[MessageChannel]:
    query = (
        db.session.query(MessageChannel)
        .join(MessageChannel.users)
        .filter(Users.id == user.id)
    )

    channels = db.session.scalars(query).all()
    return channels


def get_message_channel_details(current_user: Users, message_channel_id: int) -> dict:
    message_channel = db.session.get(MessageChannel, message_channel_id)

    messages = []
    message_schema = MessageDetailSchema()
    member_schema = MemberDetailSchema()
    for msg in message_channel.messages:
        user = db.session.get(Users, msg.author_id)

        messages.append(message_schema.load({
            "id": msg.id,
            "sender": user.display_name,
            "text": msg.content,
            "time": msg.created_at.strftime("%H:%M:%S")
        }))

    members = []
    cache_channel_key = f"message_channel_{message_channel_id}"
    channel_online_users = cache.get(cache_channel_key)
    if channel_online_users is None:
        channel_online_users = set()

    for user in message_channel.users:
        is_online = current_user.id == user.id or user.id in channel_online_users
        members.append(member_schema.load({
            "id": user.id,
            "name": user.display_name,
            "is_online": is_online
        }))

    channel_online_users.add(current_user.id)
    cache.set(cache_channel_key, channel_online_users)

    token = generate_token(current_user.id, message_channel_id, "device_identifier")

    schema = MessageChannelDetailResponseSchema()
    message_channel_details = schema.load({
        "id": message_channel.id,
        "name": ", ".join([user.display_name for user in message_channel.users]),
        "active": True,
        "created_at": message_channel.created_at.strftime("%H:%M:%S"),
        "updated_at": message_channel.updated_at.strftime("%H:%M:%S"),
        "messages": messages,
        "members": members,
    })

    return {
        "message_channel_details": message_channel_details,
        "websocket_token": token,
    }
