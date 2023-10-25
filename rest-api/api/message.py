import logging
from http.client import ACCEPTED, BAD_REQUEST, CREATED, NOT_FOUND, UNPROCESSABLE_ENTITY

from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.message import MessageSchema
import logging
from http.client import (
    ACCEPTED,
    BAD_REQUEST,
    CREATED,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
)

from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.message_channel import MessageChannelSchema
from schemas.message import MessageSchema
from models.message_channel import MessageChannel
from models.message import Message
from models.user_profile import UserProfile
from sqlalchemy.exc import NoResultFound

logger = logging.getLogger()

message_endpoints = Blueprint("Messages", __name__, url_prefix="/api/messages")


@class_route(message_endpoints, "/<int:message_channel_id>", "messages")
class MessageChannelsView(MethodView):
    # @jwt_authenticated
    def get(self, message_channel_id):
        # user = get_user_from_request(request)
        user = db.session.get(UserProfile, 2)
        channel = db.session.get(MessageChannel, message_channel_id)
        if user not in channel.users:
            return {
                f"User {user.id} is not a part of message channel {channel.id}"
            }, UNAUTHORIZED

        query = db.session.query(Message).filter(MessageChannel.id == channel.id)

        content = db.session.scalars(query).all()
        schema = MessageSchema(many=True)
        return schema.dump(content)

    # @jwt_authenticated
    def post(self, message_channel_id):
        # user = get_user_from_request(request)
        user = db.session.get(UserProfile, 2)
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = MessageSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        channel = db.session.get(MessageChannel, message_channel_id)
        if user not in channel.users:
            return {
                f"User {user.id} is not a part of message channel {channel.id}"
            }, UNAUTHORIZED

        message = Message(author=user, channel_id=channel.id, content=data["message"])
        db.session.add(message)
        db.session.commit()
        result = schema.dump(message)
        return result, CREATED
