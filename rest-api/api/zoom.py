import logging
from flask import abort, request, Blueprint
from api.constants import V1_API_PREFIX, ZOOM_EMAIL_OVERRIDE
from services.zoom import get_zoom_token, get_zoom_user_profile
from repositories.user import get_user_by_email
from http.client import (
    UNPROCESSABLE_ENTITY,
    OK,
)
from models.database import db

logger = logging.getLogger()

zoom_endpoints = Blueprint(
    "Zoom",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/zoom",
)


@zoom_endpoints.route("/callback/")
def zoom_callback():
    error = request.args.get("error", "")
    if error:
        return "Error: " + error

    code = request.args.get("code")
    access_token, refresh_token = get_zoom_token(code)
    profile_data = get_zoom_user_profile(access_token)
    authorized_email = profile_data["email"]
    authorized_email = ZOOM_EMAIL_OVERRIDE.get(authorized_email, authorized_email)
    user = get_user_by_email(authorized_email)
    if not user.is_provider:
        abort(UNPROCESSABLE_ENTITY, "only providers allow zoom integration")

    zoom_user_id = profile_data["id"]
    user.provider_profile.zoom_user_id = zoom_user_id
    user.provider_profile.zoom_refresh_token = refresh_token
    db.session.add(user.provider_profile)
    db.session.commit()
    return profile_data, OK
