import logging
from http.client import NOT_FOUND, UNPROCESSABLE_ENTITY, OK
from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, require_admin_user
from flask import Blueprint, abort, request
from flask.views import MethodView
from models.database import db
from models.appointments.appointment import Appointment, AppointmentStatus
from api.constants import V1_API_PREFIX
from services.opentok import OpenTokClient

logger = logging.getLogger()

appointment_endpoints = Blueprint(
    "Appointment",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/appointment",
)


@class_route(appointment_endpoints, "/<int:appointment_id>/", "appointment_detail")
class AppointmentDetailView(MethodView):
    @jwt_authenticated
    def get(self, appointment_id: int):
        user = get_user_from_request(request)
        appointment = db.session.get(Appointment, appointment_id)
        if appointment is None:
            abort(NOT_FOUND, "Appointment not found")
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


@appointment_endpoints.route(
    "/<int:appointment_id>/vonage-appointment-details/", methods=["GET"]
)
@jwt_authenticated
def get_video_appointment_details(appointment_id: int):
    user = get_user_from_request(request)
    appointment = db.session.get(Appointment, appointment_id)
    if appointment is None:
        abort(NOT_FOUND, "Appointment not found")
    if not (
        appointment.provider.user_id == user.id
        or appointment.patient.user_id == user.id
    ):
        require_admin_user(user)

    if not appointment.is_vonage_appointment:
        abort(
            UNPROCESSABLE_ENTITY,
            f"Appointment {appointment_id} isn't conducted through vonage",
        )
    client = OpenTokClient.instance()
    if user.is_patient:
        token = client.create_guest_token(appointment.vonage_session.session_id, user)
    else:
        token = client.create_guest_token(appointment.vonage_session.session_id, user)
    result = {"token": token}
    return result, OK
