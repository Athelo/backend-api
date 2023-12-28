
import logging
from http.client import ACCEPTED, BAD_REQUEST, CREATED, NOT_FOUND, UNPROCESSABLE_ENTITY

from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, is_current_user_or_403
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from models.user_feeling import UserFeeling
from schemas.user_feeling import UserFeelingSchema, UserFeelingUpdateSchema

logger = logging.getLogger()

user_feeling_endpoints = Blueprint(
    "My Feelings", __name__, url_prefix="/api/v1/health/"
)


@class_route(user_feeling_endpoints, "/user_feeling/", "my_feelings")
class UserFeelingsView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        feelings = (
            db.session.query(UserFeeling)
            .filter_by(user_profile_id=user.id)
            .all()
        )

        schema = UserFeelingSchema(many=True)
        return schema.dump(feelings)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserFeelingUpdateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        feeling = UserFeeling(
            occurrence_date=data["occurrence_date"],
            user_profile_id=user.id,
            note=data.get("note", None),
            general_feeling=data["general_feeling"],
        )

        db.session.add(feeling)
        db.session.commit()
        result = schema.dump(feeling)
        return result, CREATED
