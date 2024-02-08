import json

from models.users import Users
from opentok import Client, Roles, Session


class OpenTokClient(object):
    client = None

    def __init__(self, api_key: str, api_secret: str):
        self.client = Client(api_key, api_secret)

    def create_session(self) -> Session:
        return self.client.create_session()

    def create_host_token(self, session_id: str, user: Users) -> str:
        return self.create_token(
            session_id, Roles.moderator, self.create_user_metadata(user)
        )

    def create_guest_token(self, session_id: str, user: Users) -> str:
        return self.create_token(
            session_id, Roles.moderator, self.create_user_metadata(user)
        )

    def create_user_metadata(self, user: Users) -> dict:
        return json.dumps({"name": user.display_name})

    def create_token(self, session_id: str, role: Roles, metadata: dict) -> str:
        return self.client.generate_token(
            session_id=session_id, role=role, data=metadata
        )
