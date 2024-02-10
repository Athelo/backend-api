from datetime import datetime, timedelta
from http.client import UNPROCESSABLE_ENTITY

from auth.middleware import jwt_authenticated
from flask import Blueprint, abort, request
from models.appointments.appointment import Appointment, AppointmentStatus
from models.database import db
from models.provider_availability import ProviderAvailability
from models.provider_profile import ProviderProfile
from sqlalchemy import and_
from zoneinfo import ZoneInfo

from api.constants import DATETIME_FORMAT
from api.utils import generate_paginated_dict

provider_endpoints = Blueprint(
    "ProviderProfiles", __name__, url_prefix="/api/v1/providers"
)


@provider_endpoints.route("", methods=["GET"])
@jwt_authenticated
def get_all_providers():
    providers = db.session.query(ProviderProfile).all()
    return generate_paginated_dict([provider.to_json() for provider in providers])


@provider_endpoints.route("/<int:provider_profile_id>/availability/")
@jwt_authenticated
def get_provider_availability(provider_profile_id: int):
    date = request.args.get("date")
    if date is None:
        abort(UNPROCESSABLE_ENTITY, "Must provide a date")

    timezone = ZoneInfo(request.args.get("tz", default="US/Mountain"))

    start_time = datetime.strptime(date, "%m/%d/%Y")
    end_time = start_time + timedelta(days=1)
    # To account for windows that end on the following day, allow for end time to end at noon
    end_time.replace(hour=12, minute=00, second=00)

    availabilities = (
        db.session.query(ProviderAvailability)
        .filter(ProviderAvailability.provider_id == provider_profile_id)
        .filter(
            and_(
                ProviderAvailability.start_time >= start_time,
                ProviderAvailability.end_time <= end_time,
            )
        )
        .all()
    )
    appointments = (
        db.session.query(Appointment)
        .filter(Appointment.provider_id == provider_profile_id)
        .filter(
            and_(
                Appointment.start_time >= start_time,
                Appointment.end_time <= end_time,
            )
        )
        .filter(
            Appointment.status.in_(
                [AppointmentStatus.BOOKED, AppointmentStatus.IN_PROGRESS]
            )
        )
        .all()
    )

    appt_set = set([appt.start_time.strftime(DATETIME_FORMAT) for appt in appointments])

    return generate_paginated_dict(
        [
            availability.to_open_appointments_json(timezone, appt_set)
            for availability in availabilities
        ]
    )
