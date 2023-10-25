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
from models.message_channel import MessageChannel
from models.user_profile import UserProfile
from sqlalchemy.exc import NoResultFound

logger = logging.getLogger()

message_channel_endpoints = Blueprint(
    "Message Channels", __name__, url_prefix="/api/message_channels"
)


@class_route(message_channel_endpoints, "/", "message_channels")
class MessageChannelsView(MethodView):
    # @jwt_authenticated
    def get(self):
        # user = get_user_from_request(request)
        user = db.session.get(UserProfile, 2)
        query = (
            db.session.query(MessageChannel)
            .join(MessageChannel.users)
            .filter(UserProfile.id == user.id)
        )

        content = db.session.scalars(query).all()
        schema = MessageChannelSchema(many=True)
        return schema.dump(content)

    # @jwt_authenticated
    def post(self):
        # user = get_user_from_request(request)
        user = db.session.get(UserProfile, 2)
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = MessageChannelSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        participants = []
        for user_id in data["users"]:
            try:
                user = db.session.get(UserProfile, user_id)
                participants.append(user)
            except NoResultFound:
                return (
                    f"Cannot create channel because user {user_id} does not exist",
                    UNPROCESSABLE_ENTITY,
                )

        if user not in participants:
            return {
                f"Cannot make message channel for others. Current user {user.id}."
            }, UNAUTHORIZED

        channel = MessageChannel(users=participants)
        db.session.add(channel)
        db.session.commit()
        result = schema.dump(channel)
        return result, CREATED
