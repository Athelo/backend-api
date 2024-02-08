from api.appointments.appointment import appointment_endpoints
from api.appointments.appointments import appointments_endpoints
from api.appointments.providers import provider_endpoints
from api.appointments.zoom import zoom_endpoints

appointment_blueprints = [
    appointment_endpoints,
    appointments_endpoints,
    provider_endpoints,
    zoom_endpoints,
]
