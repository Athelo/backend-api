import logging
from http.client import (
    ACCEPTED,
    BAD_REQUEST,
    CREATED,
    NOT_FOUND,
    UNPROCESSABLE_ENTITY,
    UNAUTHORIZED,
)

from api.utils import class_route, generate_paginated_dict
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.user_profile import UserProfileSchema
from models.admin_profile import AdminProfile
from schemas.admin_profile import AdminProfileSchema
from api.constants import USER_PROFILE_RETURN_SCHEMA, ALLOWED_ADMIN_DOMAINS

logger = logging.getLogger()

my_profile_endpoints = Blueprint("My Profile", __name__, url_prefix="/api/v1/users/me")


@class_route(my_profile_endpoints, "/", "my_profile_detail")
class UserProfileDetailView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)

        if user:
            res = USER_PROFILE_RETURN_SCHEMA.copy()
            res["id"] = user.id
            res["first_name"] = user.first_name
            res["last_name"] = user.last_name
            res["display_name"] = user.display_name
            res["email"] = user.email
            res["is_caregiver"] = (
                user.caregiver_profiles is not None and user.caregiver_profiles.active
            )
            res["is_patient"] = (
                user.patient_profiles is not None and user.patient_profiles.active
            )
            res["is_provider"] = (
                user.provider_profiles is not None and user.provider_profiles.active
            )
            res["is_admin"] = (
                user.admin_profiles is not None and user.admin_profiles.active
            )

        return generate_paginated_dict(res)

    @jwt_authenticated
    def put(self):
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, BAD_REQUEST
        schema = UserProfileSchema(partial=True)

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, UNPROCESSABLE_ENTITY

        user = get_user_from_request(request)

        if user is None:
            return {
                "message": f"User Profile for {request.email} does not exist."
            }, NOT_FOUND

        if data.get("first_name"):
            user.first_name = data["first_name"]
        if data.get("last_name"):
            user.last_name = data["last_name"]
        if data.get("display_name"):
            user.display_name = data["display_name"]
        if data.get("email"):
            user.email = (data["email"],)
        if data.get("active"):
            user.active = (data.get("active", True),)

        db.session.add(user)
        db.session.commit()
        result = schema.dump(user)
        return result, ACCEPTED


@class_route(my_profile_endpoints, "/delete/", "delete-profile")
class UserProfileDeleteView(MethodView):
    @jwt_authenticated
    def delete(self):
        user = get_user_from_request(request)
        db.session.delete(user)
        db.session.commit()
        return {}, ACCEPTED


@class_route(my_profile_endpoints, "/admin/", "admin-profile")
class AdminProfileView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        admin_profile = (
            db.session.query(AdminProfile).filter_by(user_id=user.id).one_or_none()
        )
        if admin_profile is None:
            return {}

        schema = AdminProfileSchema()
        return schema.dump(admin_profile)

    @jwt_authenticated
    def put(self):
        user = get_user_from_request(request)

        domain = user.email.split("@")[1]

        if not any(
            allowed_domain
            for allowed_domain in ALLOWED_ADMIN_DOMAINS
            if allowed_domain == domain
        ):
            abort(UNAUTHORIZED, "user's email is not on a valid admin domain")

        admin_profile = AdminProfile(user_id=user.id)

        db.session.add(admin_profile)
        db.session.commit()

        schema = AdminProfileSchema()
        result = schema.dump(user)
        return result, ACCEPTED
