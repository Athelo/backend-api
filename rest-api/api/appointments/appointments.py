from datetime import datetime

from http.client import (
    CREATED,
    INTERNAL_SERVER_ERROR,
    UNAUTHORIZED,
)

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, require_admin_user
from flask import Blueprint, abort, request
from flask.views import MethodView
from models.appointments.appointment import Appointment, AppointmentStatus, VideoType
from models.appointments.vonage_session import VonageSession
from models.appointments.zoom_meeting import ZoomMeeting
from models.database import db
from models.users import Users
from repositories.user import get_user_by_provider_id
from repositories.utils import commit_entity
from requests.exceptions import HTTPError
from schemas.appointment import AppointmentCreateSchema
from services.opentok import OpenTokClient
from services.zoom import create_zoom_meeting_with_provider
from sqlalchemy import or_
from sqlalchemy.orm import Query
from zoneinfo import ZoneInfo

from api.constants import DATETIME_FORMAT, V1_API_PREFIX
from api.utils import class_route, generate_paginated_dict, validate_json_body

appointments_endpoints = Blueprint(
    "Appointments",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/appointments",
)


@class_route(appointments_endpoints, "/", "appointment_list")
class AppointmentListView(MethodView):
    def get_current_user_appointments_query(self, user: Users) -> Query[Appointment]:
        query = db.session.query(Appointment).filter(Appointment.status == AppointmentStatus.BOOKED)
        if user.is_provider and user.is_patient:
            query = query.filter(
                or_(
                    Appointment.patient_id == user.patient_profile.id,
                    Appointment.provider_id == user.provider_profile.id,
                )
            )
        elif user.is_provider:
            query = query.filter(Appointment.provider_id == user.provider_profile.id)
        elif user.is_patient:
            query = query.filter(Appointment.patient_id == user.patient_profile.id)
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
        video_type_arg = request.args.get("video_type")
        if video_type_arg is None:
            video_type = VideoType.VONAGE
        else:
            video_type = VideoType(video_type_arg)

        if not user.is_patient:
            abort(UNAUTHORIZED, "Only patients can book appointments")

        schema = AppointmentCreateSchema()
        data = validate_json_body(schema)

        timezone = ZoneInfo(data.get("timezone", "US/Mountain"))

        start_time = (
            data["start_time"]
            .replace(tzinfo=timezone)
            .astimezone(ZoneInfo("UTC"))
        )

        end_time = (
            data["end_time"]
            .replace(tzinfo=timezone)
            .astimezone(ZoneInfo("UTC"))
        )

        appointment = Appointment(
            patient_id=user.patient_profile.id,
            provider_id=data["provider_id"],
            start_time=start_time,
            end_time=end_time,
            status=AppointmentStatus.BOOKED,
        )

        provider = get_user_by_provider_id(data["provider_id"])

        if video_type == VideoType.ZOOM:
            try:
                zoom_appt_data = create_zoom_meeting_with_provider(
                    provider,
                    data["start_time"],
                    f"Appointment with {user.display_name}",
                )
                appointment.zoom_meeting = ZoomMeeting(
                    zoom_host_url=zoom_appt_data["start_url"],
                    zoom_join_url=zoom_appt_data["join_url"],
                )
            except HTTPError as exc:
                abort(
                    INTERNAL_SERVER_ERROR,
                    f"Failed to create zoom meeting - {exc.response}",
                )

        if video_type == VideoType.VONAGE:
            try:
                client = OpenTokClient.instance()
                session = client.create_session()
                appointment.vonage_session = VonageSession(
                    session_id=session.session_id
                )
            except Exception as exc:
                abort(
                    INTERNAL_SERVER_ERROR,
                    f"Failed to create zoom meeting - {exc.response}",
                )

        commit_entity(appointment)

        # result = AppointmentSchema().dump(appointment)
        result = appointment.to_legacy_json()
        return result, CREATED
