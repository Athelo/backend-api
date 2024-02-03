from datetime import datetime
from http.client import (
    ACCEPTED,
    BAD_REQUEST,
    CREATED,
    NOT_FOUND,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
)

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.admin_profile import AdminProfile
from models.database import db
from models.patient_profile import PatientProfile
from models.provider_availability import ProviderAvailability
from models.provider_profile import ProviderProfile, ProviderType
from repositories.user import create_admin_profile_for_user
from repositories.utils import commit_entity
from schemas.admin_profile import AdminProfileSchema
from schemas.patient_profile import PatientProfileCreateSchema, PatientProfileSchema
from schemas.provider_profile import ProviderProfileCreateSchema, ProviderProfileSchema
from schemas.user_profile import UserProfileSchema
from zoneinfo import ZoneInfo

from api.constants import (
    DATETIME_FORMAT,
    USER_PROFILE_RETURN_SCHEMA,
)
from api.utils import class_route, generate_paginated_dict

my_profile_endpoints = Blueprint("My Profile", __name__, url_prefix="/api/v1/users/me")


@class_route(my_profile_endpoints, "/", "my_profile_detail")
class UserProfileDetailView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)

        if not user:
            abort(NOT_FOUND, "user not found for email")

        res = USER_PROFILE_RETURN_SCHEMA.copy()
        res["id"] = user.id
        res["first_name"] = user.first_name
        res["last_name"] = user.last_name
        res["display_name"] = user.display_name
        res["email"] = user.email
        res["birthday"] = user.birthday
        res["phone"] = user.phone
        res["is_caregiver"] = user.is_caregiver
        res["is_patient"] = user.is_patient
        res["is_provider"] = user.is_provider
        res["is_admin"] = user.is_admin

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

        # Add TODO to remove later
        if data.get("first_name"):
            user.first_name = data["first_name"]
        if data.get("last_name"):
            user.last_name = data["last_name"]
        if data.get("display_name"):
            user.display_name = data["display_name"]
        if data.get("birthday"):
            user.birthday = data["birthday"]
        if data.get("phone"):
            user.phone = data["phone"]
        if data.get("active"):
            user.active = (data.get("active", True),)
        commit_entity(user)
        result = schema.dump(user)
        return result, ACCEPTED


@class_route(my_profile_endpoints, "/delete/", "delete-profile")
class UserProfileDeleteView(MethodView):
    @jwt_authenticated
    def delete(self):
        user = get_user_from_request(request)
        user.active = False
        # db.session.delete(user)
        # db.session.commit()
        return {"message": "Attempted to delete the user"}, ACCEPTED


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
        create_admin_profile_for_user(user)

        schema = AdminProfileSchema()
        result = schema.dump(user.admin_profile)
        return result, ACCEPTED


@class_route(my_profile_endpoints, "/patient/", "patient-profile")
class PatientProfileView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        patient_profile = (
            db.session.query(PatientProfile).filter_by(user_id=user.id).one_or_none()
        )
        if patient_profile is None:
            return {}

        schema = PatientProfileSchema()
        return schema.dump(patient_profile)

    @jwt_authenticated
    def put(self):
        user = get_user_from_request(request)
        json_data = request.get_json()
        if not json_data:
            abort(BAD_REQUEST, "No input data provided.")
        schema = PatientProfileCreateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            abort(UNPROCESSABLE_ENTITY, err.messages)

        cancer_status = data["cancer_status"]

        if user.is_patient:
            user.patient_profile.cancer_status = cancer_status
            patient_profile = user.patient_profile
        else:
            patient_profile = PatientProfile(
                user_id=user.id, cancer_status=cancer_status
            )
        commit_entity(patient_profile)

        schema = PatientProfileSchema()
        result = schema.dump(patient_profile)
        return result, ACCEPTED


@class_route(my_profile_endpoints, "/provider/", "provider-profile")
class ProviderProfileView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        provider_profile = (
            db.session.query(ProviderProfile).filter_by(user_id=user.id).one_or_none()
        )
        if provider_profile is None:
            return {}

        schema = ProviderProfileSchema()
        return schema.dump(provider_profile)

    @jwt_authenticated
    def put(self):
        user = get_user_from_request(request)
        json_data = request.get_json()
        if not json_data:
            abort(BAD_REQUEST, "No input data provided.")
        schema = ProviderProfileCreateSchema()

        try:
            data = schema.load(json_data)
            provider_type = ProviderType(data["provider_type"])

        except ValidationError as err:
            abort(UNPROCESSABLE_ENTITY, err.messages)

        appointment_buffer = data["appointment_buffer_sec"]

        if user.is_provider:
            provider_profile = user.provider_profile
            provider_profile.appointment_buffer_sec = appointment_buffer
            provider_profile.provider_type = provider_type
        else:
            provider_profile = ProviderProfile(
                user_id=user.id,
                appointment_buffer_sec=appointment_buffer,
                provider_type=provider_type,
            )

        commit_entity(provider_profile)

        schema = ProviderProfileSchema()
        result = schema.dump(provider_profile)
        return result, ACCEPTED


@class_route(my_profile_endpoints, "/availability/", "my-availability")
class ProviderAvailabilityView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        if not user.is_provider:
            abort(UNAUTHORIZED, "Only providers have availability")

        timezone = ZoneInfo(request.args.get("tz", default="US/Mountain"))

        availabilities = (
            db.session.query(ProviderAvailability)
            .filter(ProviderAvailability.provider_id == user.provider_profile.id)
            .filter(
                ProviderAvailability.end_time > datetime.utcnow(),
            )
            .all()
        )
        # TODO: remove booked appts from availability

        return generate_paginated_dict(
            [availability.to_json(timezone) for availability in availabilities]
        )

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        if not user.is_provider:
            abort(UNAUTHORIZED, "Only providers have availability")

        timezone = ZoneInfo(request.args.get("tz", default="US/Mountain"))

        json_data = request.get_json()
        start_time = (
            datetime.strptime(json_data["start_time"], DATETIME_FORMAT)
            .replace(tzinfo=timezone)
            .astimezone(ZoneInfo("UTC"))
        )

        end_time = (
            datetime.strptime(json_data["end_time"], DATETIME_FORMAT)
            .replace(tzinfo=timezone)
            .astimezone(ZoneInfo("UTC"))
        )

        availability = ProviderAvailability(
            provider_id=user.provider_profile.id,
            start_time=start_time,
            end_time=end_time,
        )
        commit_entity(availability)
        result = availability.to_json(timezone)
        return result, CREATED


@my_profile_endpoints.route("/availability/<int:availability_id>/", methods=["DELETE"])
@jwt_authenticated
def delete_availability(availability_id: int):
    user = get_user_from_request(request)

    availability = db.session.get(ProviderAvailability, availability_id)
    if availability.provider_id != user.provider_profile.id and not user.is_admin:
        abort(UNAUTHORIZED, "Cannot delete availability for another provider")

    db.session.delete(availability)
    db.session.commit()
    return {}, ACCEPTED
