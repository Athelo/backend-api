import logging
from flask import abort, request, Blueprint
from api.utils import commit_entity_or_abort
from api.constants import V1_API_PREFIX
from services.zoom import (
    get_zoom_token,
    get_zoom_user_profile,
    get_zoom_users_for_account,
)
from repositories.user import get_user_by_email, update_provider_zoom_id_by_email
from http.client import (
    UNPROCESSABLE_ENTITY,
    OK,
)
from auth.middleware import jwt_authenticated
from auth.utils import require_admin_user

logger = logging.getLogger()

zoom_endpoints = Blueprint(
    "Zoom",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/zoom",
)


@zoom_endpoints.route("/callback")
def zoom_callback():
    error = request.args.get("error", "")
    if error:
        return "Error: " + error

    code = request.args.get("code")
    access_token, refresh_token = get_zoom_token(code)
    profile_data = get_zoom_user_profile(access_token)
    authorized_email = profile_data["email"]
    user = get_user_by_email(authorized_email)
    if not user.is_provider:
        abort(UNPROCESSABLE_ENTITY, "only providers allow zoom integration")

    zoom_user_id = profile_data["id"]
    user.provider_profile.zoom_user_id = zoom_user_id
    user.provider_profile.zoom_refresh_token = refresh_token
    commit_entity_or_abort(user.provider_profile)

    return profile_data, OK


@zoom_endpoints.route("/update_users_zoom_info/")
@jwt_authenticated
def get_zoom_account_users():
    user = get_user_by_email(request.email)
    require_admin_user(user)
    zoom_users = get_zoom_users_for_account()
    updated_users = []
    for zoom_user in zoom_users:
        print(zoom_user)
        email = zoom_user["email"]
        zoom_id = zoom_user["id"]
        if update_provider_zoom_id_by_email(email, zoom_id):
            updated_users.append(email)

    return updated_users, OK
