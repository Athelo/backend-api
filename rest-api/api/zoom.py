import logging
from flask import Flask, abort, request, Blueprint
from api.constants import V1_API_PREFIX
from services.zoom import get_zoom_token, get_zoom_user_email
from repositories.user import get_user_by_email

CLIENT_ID = "uGg_8H7qSYmioNsz2I83aA"  # Fill this in with your client ID
CLIENT_SECRET = "dTJBejFCWnBRRkdqbW9yaTM1MkR0UTpWNDhIMGNwTzVyWjcxVk5LczlQeHMzQ0dYYzV4MTJUUw"  # Fill this in with your client secret
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
    access_token = get_zoom_token(code)
    # Note: In most cases, you'll want to store the access token, in, say,
    # a session for use in other parts of your web app.
    authorized_email = get_zoom_user_email(access_token)
    user = get_user_by_email(authorized_email)
    return "Your user info is: %s" % get_zoom_username(access_token)
