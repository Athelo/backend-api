from http.client import BAD_REQUEST, CREATED, UNPROCESSABLE_ENTITY, NOT_FOUND, ACCEPTED
import logging
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from schemas.user_profile import UserProfileSchema
from models import db
from models.user_profile import UserProfile
from api.utils import class_route

logger = logging.getLogger()
# Create a user blueprint
user_profile_endpoints = Blueprint("User Profiles", __name__, url_prefix="/api/users")


@class_route(user_profile_endpoints, "/", "user_profiles")
class UserProfilesView(MethodView):
    def get(self):
        users = db.session.scalars(db.select(UserProfile)).all()
        schema = UserProfileSchema(many=True)
        return schema.dump(users)

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
    def get(self, user_profile_id):
        user = db.session.get(UserProfile, user_profile_id)
        schema = UserProfileSchema()
        return schema.dump(user)

    def put(self, user_profile_id):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserProfileSchema(partial=True)

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        user = db.session.get(UserProfile, user_profile_id)
        if user is None:
            return {
                "message": f"User Profile {user_profile_id} does not exist."
            }, NOT_FOUND

        if data.get("first_name"):
            user.first_name = data["first_name"]
        if data.get("last_name"):
            user.last_name = data["last_name"]
        if data.get("display_name"):
            user.display_name = (data.get("display_name", None),)
        if data.get("email"):
            user.email = (data["email"],)
        if data.get("active"):
            user.active = (data.get("active", True),)

        db.session.add(user)
        db.session.commit()
        result = schema.dump(user)
        return result, ACCEPTED


# @symptom_endpoints.route("/symptoms", methods=["GET"])
# def symptoms():
#     symptoms = db.session.scalars(db.select(Symptom)).all()
#     schema = SymptomSchema()
#     return schema.dump(symptoms)

# @symptom_endpoints.route("/symptoms", methods=["POST"])
# def create_symptom():
#     symptom = S
#     symptoms = db.session.scalars(db.select(Symptom)).all()
#     schema = SymptomSchema()
#     return schema.dump(symptoms)
