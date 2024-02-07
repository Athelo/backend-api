from __future__ import annotations

from http.client import REQUEST_ENTITY_TOO_LARGE, UNAUTHORIZED, UNPROCESSABLE_ENTITY

from flask import abort

from api.appointment import appointment_endpoints
from api.appointments import appointments_endpoints
from api.common import common_endpoints
from api.feedback import feedback_endpoints
from api.images import image_endpoints
from api.main import main_endpoints
from api.message import message_endpoints
from api.message_channel import message_channel_endpoints
from api.messaging.community_thread import community_thread_endpoints
from api.messaging.thread_post import thread_post_endpoints
from api.my_profile import my_profile_endpoints
from api.providers import provider_endpoints
from api.saved_content import saved_content_endpoints
from api.symptom import symptom_endpoints
from api.user_feeling import user_feeling_endpoints
from api.user_feelings_and_symptoms import user_feeling_and_symptom_endpoints
from api.user_profile import user_profile_endpoints
from api.user_symptom import user_symptom_endpoints
from api.zoom import zoom_endpoints

blueprints = [
    appointment_endpoints,
    appointments_endpoints,
    common_endpoints,
    community_thread_endpoints,
    feedback_endpoints,
    main_endpoints,
    message_endpoints,
    message_channel_endpoints,
    my_profile_endpoints,
    provider_endpoints,
    saved_content_endpoints,
    symptom_endpoints,
    user_feeling_endpoints,
    user_feeling_and_symptom_endpoints,
    user_profile_endpoints,
    user_symptom_endpoints,
    zoom_endpoints,
    image_endpoints,
    thread_post_endpoints,
]


def handle_database_error(e):
    return (
        f"Cannot create db entity because {e.orig.args[0]['M']}",
        UNPROCESSABLE_ENTITY,
    )


def handle_unauthorized(e):
    return e.message, UNAUTHORIZED


def too_large(e):
    return "File is too large", REQUEST_ENTITY_TOO_LARGE
