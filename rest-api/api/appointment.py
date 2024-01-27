import logging
from http.client import (
    BAD_REQUEST,
    CREATED,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
)
from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, require_admin_user
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.appointment import AppointmentSchema, AppointmentCreateSchema
from models.appointment import Appointment, AppointmentStatus
from sqlalchemy.exc import IntegrityError, DatabaseError
from api.constants import V1_API_PREFIX

logger = logging.getLogger()

appointment_endpoints = Blueprint(
    "Appointment",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/appointment",
)


@jwt_authenticated
@appointment_endpoints.route("/", methods=["POST"])
def create_appointment():
    user = get_user_from_request(request)
    if not user.is_patient:
        abort(UNAUTHORIZED, "Only patients can book appointments")

    json_data = request.get_json()
    if not json_data:
        abort(BAD_REQUEST, "No input data provided.")
    schema = AppointmentCreateSchema()

    try:
        data = schema.load(json_data)
    except ValidationError as err:
        abort(UNPROCESSABLE_ENTITY, err.messages)

    appointment = Appointment(
        patient_id=user.patient_profile.id,
        provider_id=data["provider_id"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        zoom_url=data["zoom_url"],
        zoom_token=data["zoom_token"],
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


@class_route(appointment_endpoints, "/<int:appointment_id/", "appointment_detail")
class AppointmentDetailView(MethodView):
    @jwt_authenticated
    def get(self, appointment_id: int):
        user = get_user_from_request(request)
        appointment = db.session.get(Appointment, appointment_id)
        if not (
            appointment.provider.user_id == user.id
            or appointment.patient.user_id == user.id
        ):
            require_admin_user(user)

        return appointment.to_legacy_json()

    @jwt_authenticated
    def delete(self, appointment_id: int):
        user = get_user_from_request(request)
        appointment = db.session.get(Appointment, appointment_id)
        if not (
            appointment.provider.user_id == user.id
            or appointment.patient.user_id == user.id
        ):
            require_admin_user(user)

        appointment.status = AppointmentStatus.CANCELLED
