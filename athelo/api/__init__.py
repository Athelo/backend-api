from __future__ import annotations

from api.main import main_endpoints
from api.symptom import symptom_endpoints
from api.user_profile import user_profile_endpoints
from api.user_symptom import user_symptom_endpoints
from api.my_profile import my_profile_endpoints
from api.saved_content import saved_content_endpoints

blueprints = [
    main_endpoints,
    symptom_endpoints,
    user_profile_endpoints,
    user_symptom_endpoints,
    my_profile_endpoints,
    saved_content_endpoints,
]
