import logging
from http.client import (
    BAD_REQUEST,
    CREATED,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
    INTERNAL_SERVER_ERROR,
)
from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, require_admin_user
from models.users import Users
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.appointment import AppointmentSchema, AppointmentCreateSchema
from models.appointment import Appointment, AppointmentStatus
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy import or_
from sqlalchemy.orm import Query
from api.constants import V1_API_PREFIX
from api.utils import generate_paginated_dict
from services.zoom import create_zoom_meeting_with_provider
from requests.exceptions import HTTPError
from repositories.user import get_user_by_provider_id

logger = logging.getLogger()

appointments_endpoints = Blueprint(
    "Appointments",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/appointments",
)


@class_route(appointments_endpoints, "/", "appointment_list")
class AppointmentListView(MethodView):
    def get_current_user_appointments_query(self, user: Users) -> Query[Appointment]:
        query = db.session.query(Appointment)
        if user.is_provider and user.is_patient:
            query.filter(
                or_(
                    Appointment.patient_id == user.patient_profile.id,
                    Appointment.provider_id == user.provider_profile.id,
                )
            )
        elif user.is_provider:
            query.filter(Appointment.provider_id == user.provider_profile.id)
        elif user.is_patient:
            query.filter(Appointment.patient_id == user.patient_profile.id)
        else:
            return None
        return query

    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        fetch_all = request.args.get("all", type=bool, default=False)
        query = db.session.query(Appointment)
        if fetch_all:
            require_admin_user(user)
        else:
            query = self.get_current_user_appointments_query(user)

        appts = query.all()
        results = [appointment.to_legacy_json() for appointment in appts]
        return generate_paginated_dict(results)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        if not user.is_patient:
            abort(UNAUTHORIZED, "Only patients can book appointments")

        json_data = request.get_json()
        if not json_data:
            abort(BAD_REQUEST, "No input data provided.")
        schema = AppointmentCreateSchema()

        try:
            request_data = schema.load(json_data)
        except ValidationError as err:
            abort(UNPROCESSABLE_ENTITY, err.messages)

        provider = get_user_by_provider_id(request_data["provider_id"])
        try:
            zoom_appt_data = create_zoom_meeting_with_provider(
                provider,
                request_data["start_time"],
                f"Appointment with {user.display_name}",
            )
        except HTTPError as exc:
            abort(
                INTERNAL_SERVER_ERROR, f"Failed to create zoom meeting - {exc.response}"
            )

        appointment = Appointment(
            patient_id=user.patient_profile.id,
            provider_id=request_data["provider_id"],
            start_time=request_data["start_time"],
            end_time=request_data["end_time"],
            zoom_host_url=zoom_appt_data["start_url"],
            zoom_join_url=zoom_appt_data["join_url"],
            status=AppointmentStatus.BOOKED,
        )
        try:
            db.session.add(appointment)
            db.session.commit()
        except IntegrityError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create appointment because {e.orig.args[0]['M']}",
            )
        except DatabaseError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create appointment because {e.orig.args[0]['M']}",
            )
        result = AppointmentSchema().dump(appointment)
        return result, CREATED
