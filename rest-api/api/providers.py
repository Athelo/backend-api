from http.client import UNPROCESSABLE_ENTITY

from sqlalchemy import or_

from api.utils import generate_paginated_dict
from auth.middleware import jwt_authenticated
from flask import Blueprint, abort, request
from models.database import db
from models.provider_profile import ProviderProfile
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from models.provider_availability import ProviderAvailability


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

    start_time = (
        datetime.strptime(date, "%m/%d/%Y")
        .replace(tzinfo=timezone)
        .astimezone(ZoneInfo("UTC"))
    )
    end_time = start_time + timedelta(days=1)

    availabilities = (
        db.session.query(ProviderAvailability)
        .filter(ProviderAvailability.provider_id == provider_profile_id)
        .filter(
            or_(
                ProviderAvailability.start_time > start_time,
                ProviderAvailability.end_time < end_time,
            )
        )
        .all()
    )
    # TODO: remove booked appts from availability

    return generate_paginated_dict(
        [
            availability.to_open_appointments_json(timezone)
            for availability in availabilities
        ]
    )
