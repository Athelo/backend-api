from http.client import CREATED, UNPROCESSABLE_ENTITY

from auth.middleware import jwt_authenticated
from auth.utils import require_admin_user
from flask import Blueprint, request
from flask.views import MethodView
from models.database import db
from models.users import Users
from repositories.user import (
    create_admin_profile_for_user,
    create_caregiver_profile_for_user,
    create_patient_profile_for_user,
    create_provider_profile_for_user,
    get_user_by_email,
)
from repositories.utils import commit_entity
from schemas.admin_profile import AdminProfileSchema
from schemas.caregiver_profile import CaregiverProfileSchema
from schemas.patient_profile import PatientProfileSchema
from schemas.provider_profile import ProviderProfileSchema
from schemas.user_profile import UserProfileCreateSchema, UserProfileSchema

from api.constants import V1_API_PREFIX
from api.utils import class_route, generate_paginated_dict, validate_json_body

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
        schema = UserProfileCreateSchema()

        data = validate_json_body(schema)
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
    require_admin_user(get_user_by_email(request.email))
    user = db.session.get(Users, user_id)
    create_admin_profile_for_user(user)

    schema = AdminProfileSchema()
    result = schema.dump(user.admin_profile)
    return result


@user_profile_endpoints.route("/<int:user_id>/provider", methods=["PUT"])
@jwt_authenticated
def create_provider(user_id: int):
    require_admin_user(get_user_by_email(request.email))
    user = db.session.get(Users, user_id)

    create_provider_profile_for_user(user)

    schema = ProviderProfileSchema()
    result = schema.dump(user.admin_profile)
    return result


@user_profile_endpoints.route("/<int:user_id>/patient", methods=["PUT"])
@jwt_authenticated
def create_patient(user_id: int):
    require_admin_user(get_user_by_email(request.email))
    user = db.session.get(Users, user_id)
    create_patient_profile_for_user(user)

    schema = PatientProfileSchema()
    result = schema.dump(user.admin_profile)
    return result


@user_profile_endpoints.route("/<int:user_id>/caregiver", methods=["PUT"])
@jwt_authenticated
def create_caregiver(user_id: int):
    require_admin_user(get_user_by_email(request.email))
    user = db.session.get(Users, user_id)
    create_caregiver_profile_for_user(user)

    schema = CaregiverProfileSchema()
    result = schema.dump(user.admin_profile)
    return result
