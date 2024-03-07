from __future__ import annotations

from http.client import REQUEST_ENTITY_TOO_LARGE, UNAUTHORIZED, UNPROCESSABLE_ENTITY

from auth.exceptions import UnauthorizedException
from flask import current_app as app
from sqlalchemy.exc import DatabaseError, IntegrityError

from api.appointments import appointment_blueprints
from api.common import common_endpoints
from api.feedback import feedback_endpoints
from api.health import health_blueprints
from api.images import image_endpoints
from api.main import main_endpoints
from api.message import message_endpoints
from api.message_channel import message_channel_endpoints
from api.messaging import messaging_blueprints
from api.my_profile import my_profile_endpoints
from api.saved_content import saved_content_endpoints
from api.socket_connection import socket_endpoints
from api.user_feeling import user_feeling_endpoints
from api.user_feelings_and_symptoms import user_feeling_and_symptom_endpoints
from api.user_profile import user_profile_endpoints
from api.webapp import webapp_endpoints

blueprints = (
    [
        common_endpoints,
        feedback_endpoints,
        main_endpoints,
        message_endpoints,
        message_channel_endpoints,
        my_profile_endpoints,
        saved_content_endpoints,
        user_feeling_endpoints,
        user_feeling_and_symptom_endpoints,
        user_profile_endpoints,
        image_endpoints,
        socket_endpoints,
        webapp_endpoints,
    ]
    + appointment_blueprints
    + messaging_blueprints
    + health_blueprints
)


def log_error(e):
    print(e)
    app.logger.error(e)


def handle_database_error(e):
    log_error(e)
    return (
        f"Cannot create db entity because {e.orig.args[0]['M']}",
        UNPROCESSABLE_ENTITY,
    )


def handle_unauthorized(e):
    log_error(e)
    return e.message, UNAUTHORIZED


def too_large(e):
    log_error(e)
    return "File is too large", REQUEST_ENTITY_TOO_LARGE


error_handler_mapping = {
    handle_database_error: [DatabaseError, IntegrityError],
    handle_unauthorized: [UnauthorizedException],
    too_large: [413],
}
