import logging
from http.client import ACCEPTED, BAD_REQUEST, CREATED, NOT_FOUND, UNPROCESSABLE_ENTITY

from api.utils import class_route
from auth.middleware import jwt_authenticated
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from models.user_profile import UserProfile
from schemas.user_profile import UserProfileSchema

logger = logging.getLogger()

user_profile_endpoints = Blueprint("User Profiles", __name__, url_prefix="/api/users")


@class_route(user_profile_endpoints, "/", "user_profiles")
class UserProfilesView(MethodView):
    @jwt_authenticated
    def get(self):
        users = db.session.scalars(db.select(UserProfile)).all()
        schema = UserProfileSchema(many=True)
        return schema.dump(users)

    @jwt_authenticated
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserProfileSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        user_profile = UserProfile(
            first_name=data["first_name"],
            last_name=data["last_name"],
            display_name=data.get("display_name", None),
            email=data["email"],
            active=data.get("active", True),
        )
        db.session.add(user_profile)
        db.session.commit()
        result = schema.dump(user_profile)
        return result, CREATED


@class_route(user_profile_endpoints, "/<user_profile_id>", "user_profile_detail")
class UserProfileDetailView(MethodView):
    @jwt_authenticated
    def get(self, user_profile_id):
        user = db.session.get(UserProfile, user_profile_id)
        schema = UserProfileSchema()
        return schema.dump(user)
