import logging
from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, request, jsonify
from flask.views import MethodView

from models.database import db
from schemas.message_channel import MessageChannelSchema
from models.message_channel import MessageChannel

from use_cases.message_channel_use_case import get_message_channel_details, \
    validate_message_channel_request_participants, validate_message_channel_request_data, get_participants_hash, \
    get_message_channels_for_user, create_message_channel

logger = logging.getLogger()

message_channel_endpoints = Blueprint(
    "Message Channels", __name__, url_prefix="/api/v1/message-channels"
)


@class_route(message_channel_endpoints, "/", "message_channels")
class MessageChannelsView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        channels = get_message_channels_for_user(user)
        schema = MessageChannelSchema(many=True)
        return schema.dump(channels)

    @jwt_authenticated
    def post(self):
        data = validate_message_channel_request_data(request)
        participants = validate_message_channel_request_participants(request, data)
        channel = create_message_channel(participants)
        result = MessageChannelSchema().dump(channel)
        return result


@message_channel_endpoints.get("/<message_channel_id>/")
@jwt_authenticated
def get_message_channel_detail(message_channel_id: int):
    message_channel_id = int(message_channel_id)
    current_user = get_user_from_request(request)

    result = get_message_channel_details(current_user, message_channel_id)
    return jsonify(result)


@message_channel_endpoints.route("/search/", methods=["POST"])
@jwt_authenticated
def find_channel_by_members():
    data = validate_message_channel_request_data(request)
    participants = validate_message_channel_request_participants(request, data)
    channel = (
        db.session.query(MessageChannel)
        .filter(MessageChannel.users_hash == get_participants_hash(participants))
        .one_or_none()
    )
    return MessageChannelSchema().dump(channel)
