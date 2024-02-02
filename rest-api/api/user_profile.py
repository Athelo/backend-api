from http.client import BAD_REQUEST, CREATED, UNPROCESSABLE_ENTITY

from api.utils import class_route, generate_paginated_dict
from repositories.utils import commit_entity
from auth.middleware import jwt_authenticated
from flask import Blueprint, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from models.users import Users
from schemas.user_profile import UserProfileSchema, UserProfileCreateSchema
from schemas.admin_profile import AdminProfileSchema
from repositories.user import get_user_by_email
from api.constants import V1_API_PREFIX
from repositories.user import create_admin_profile_for_user


user_profile_endpoints = Blueprint(
    "User Profiles", __name__, url_prefix=f"{V1_API_PREFIX}/users"
)


@class_route(user_profile_endpoints, "/user-profiles/", "user_profiles")
class UserProfilesView(MethodView):
    @jwt_authenticated
    def get(self):
        users = db.session.query(Users).all()
        schema = UserProfileSchema()
        res = [schema.dump(user) for user in users]
        return generate_paginated_dict(res)

    @jwt_authenticated
    def post(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserProfileCreateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        # check for existing user
        user = get_user_by_email(request.email)

        if user is not None:
            return "User with that email already exists", UNPROCESSABLE_ENTITY

        user_profile = Users(
            first_name=data["first_name"],
            last_name=data["last_name"],
            display_name=data["display_name"],
            email=request.email,
            active=data.get("active", True),
        )
        commit_entity(user_profile)
        result = UserProfileSchema().dump(user_profile)
        return result, CREATED


@class_route(
    user_profile_endpoints, "/user-profiles/<user_profile_id>/", "user_profile_detail"
)
class UserProfileDetailView(MethodView):
    @jwt_authenticated
    def get(self, user_profile_id):
        user = db.session.get(Users, user_profile_id)
        schema = UserProfileSchema()
        return schema.dump(user)


@user_profile_endpoints.route("/<int:user_id>/admin", methods=["PUT"])
@jwt_authenticated
def create_admin(user_id: int):
    user = db.session.get(Users, user_id)
    create_admin_profile_for_user(user)

    schema = AdminProfileSchema()
    result = schema.dump(user.admin_profile)
    return result
