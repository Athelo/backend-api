from __future__ import annotations

from api.main import main_endpoints
from api.common import common_endpoints
from api.my_profile import my_profile_endpoints
from api.saved_content import saved_content_endpoints
from api.socket_connection import socket_endpoints
from api.symptom import symptom_endpoints
from api.user_profile import user_profile_endpoints
from api.user_feeling import user_feeling_endpoints
from api.user_symptom import user_symptom_endpoints
from api.message import message_endpoints
from api.message_channel import message_channel_endpoints
from api.community_thread import community_thread_endpoints
from api.feedback import feedback_endpoints
from api.appointments import appointments_endpoints
from api.providers import provider_endpoints
from api.appointment import appointment_endpoints
from api.zoom import zoom_endpoints

blueprints = [
    main_endpoints,
    common_endpoints,
    symptom_endpoints,
    user_feeling_endpoints,
    user_profile_endpoints,
    user_symptom_endpoints,
    my_profile_endpoints,
    saved_content_endpoints,
    message_endpoints,
    message_channel_endpoints,
    community_thread_endpoints,
    socket_endpoints,
    feedback_endpoints,
    appointments_endpoints,
    provider_endpoints,
    appointment_endpoints,
    zoom_endpoints,
]
