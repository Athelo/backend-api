import logging
from http.client import (
    BAD_REQUEST,
    CREATED,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
    CONFLICT,
    NOT_FOUND,
    OK,
)
from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, require_admin_user
from models.users import Users
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.appointment import (
    AppointmentSchema,
)
from models.appointment import Appointment
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlalchemy import or_
from sqlalchemy.orm import Query
from api.constants import V1_API_PREFIX
from api.utils import generate_paginated_dict

logger = logging.getLogger()

appointments_endpoints = Blueprint(
    "Appointments",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/appointments",
)


def appointment_to_json(appointment: Appointment):
    return {
        "provider": {"display_name": appointment.provider.display_name, "photo": ""},
        "patient": {"display_name": appointment.patient.display_name, "photo": ""},
        "start_time": appointment.start_time,
        "end_time": appointment.end_time,
        "zoom_url": appointment.zoom_url,
        "zoom_token": appointment.zoom_token,
    }


@class_route(appointments_endpoints, "/", "appointment_list")
class AppointmentListView(MethodView):
    def get_current_user_appointments_query(self, user: Users) -> Query[Appointment]:
        query = db.session.query(Appointment)
        if user.is_provider() and user.is_patient():
            query.filter(
                or_(
                    Appointment.patient_id == user.patient_profile.id,
                    Appointment.provider_id == user.provider_profile.id,
                )
            )
        elif user.is_provider():
            query.filter(Appointment.provider_id == user.provider_profile.id)
        elif user.is_patient():
            query.filter(Appointment.patient_id == user.patient_profile.id)
        else:
            return None

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
        results = [appointment_to_json(appointment) for appointment in appts]
        return generate_paginated_dict(results)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        if not user.is_patient():
            abort(UNAUTHORIZED, "Only patients can book appointments")

        json_data = request.get_json()
        if not json_data:
            abort(BAD_REQUEST, "No input data provided.")
        schema = AppointmentSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            abort(UNPROCESSABLE_ENTITY, err.messages)

        appointment = Appointment(
            patient_id=user.id,
            provider_id=data["provider_id"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            zoom_url=data["zoom_url"],
            zoom_token=data["zoom_token"],
        )
        try:
            db.session.add(appointment)
            db.session.commit()
        except IntegrityError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create appointment because {e.orig.args[0]['M']}",
            )
        result = schema.dump(appointment)
        return result, CREATED
