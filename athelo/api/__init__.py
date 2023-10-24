from __future__ import annotations

from api.main import main_endpoints
from api.vote import vote_endpoints
from api.symptom import symptom_endpoints
from api.user_profile import user_profile_endpoints
from api.user_symptom import user_symptom_endpoints

blueprints = [
    main_endpoints,
    vote_endpoints,
    symptom_endpoints,
    user_profile_endpoints,
    user_symptom_endpoints,
]
