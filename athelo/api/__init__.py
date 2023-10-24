from __future__ import annotations

from api.main import main_endpoints
from api.vote import vote_endpoints

blueprints = [main_endpoints, vote_endpoints]
