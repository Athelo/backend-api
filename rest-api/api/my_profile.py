import logging
from http.client import (
    ACCEPTED,
    BAD_REQUEST,
    NOT_FOUND,
    UNPROCESSABLE_ENTITY,
    UNAUTHORIZED,
    CREATED,
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
from models.patient_profile import PatientProfile
from schemas.patient_profile import PatientProfileCreateSchema, PatientProfileSchema
from models.provider_profile import ProviderProfile
from schemas.provider_profile import ProviderProfileSchema, ProviderProfileCreateSchema
from api.constants import (
    USER_PROFILE_RETURN_SCHEMA,
    ALLOWED_ADMIN_DOMAINS,
    DATETIME_FORMAT,
)
from zoneinfo import ZoneInfo
from datetime import datetime
from models.provider_availability import ProviderAvailability
from sqlalchemy.exc import DatabaseError, IntegrityError

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
        result = schema.dump(admin_profile)
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

        db.session.add(patient_profile)
        db.session.commit()

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
        except ValidationError as err:
            abort(UNPROCESSABLE_ENTITY, err.messages)

        appointment_buffer = data["appointment_buffer_sec"]

        if user.is_provider:
            user.provider_profile.appointment_buffer_sec = appointment_buffer
            provider_profile = user.provider_profile
        else:
            provider_profile = ProviderProfile(
                user_id=user.id, appointment_buffer_sec=appointment_buffer
            )

        db.session.add(provider_profile)
        db.session.commit()

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

        try:
            db.session.add(availability)
            db.session.commit()
        except IntegrityError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create feedback topic because {e.orig.args[0]['M']}",
            )
        except DatabaseError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create feedback topic because {e.orig.args[0]['M']}",
            )
        result = availability.to_json(timezone)
        return result, CREATED
