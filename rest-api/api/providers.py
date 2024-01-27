import logging
from http.client import ACCEPTED, BAD_REQUEST, CREATED, NOT_FOUND, UNPROCESSABLE_ENTITY

from sqlalchemy import or_

from api.utils import class_route, generate_paginated_dict
from auth.middleware import jwt_authenticated
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from models.users import Users
from models.provider_profile import ProviderProfile
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from models.provider_availability import ProviderAvailability

logger = logging.getLogger()

provider_endpoints = Blueprint(
    "ProviderProfiles", __name__, url_prefix="/api/v1/providers"
)


@jwt_authenticated
@provider_endpoints.route("", methods=["GET"])
def get_all_providers():
    providers = db.session.query(ProviderProfile).all()
    return generate_paginated_dict([provider.to_json() for provider in providers])


@jwt_authenticated
@provider_endpoints.route("/<int:provider_profile_id>/availability/")
def get_provider_availability(provider_profile_id: int):
    date = request.args.get("date")
    print(date)
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
