import json

from flask import Flask
from models.users import Users
from opentok import Client, Roles, Session


class OpenTokClient(object):
    client = None

    def _require_init(self):
        if self.client is None:
            raise Exception("Class has not been initialized")

    def init_app(self, app: Flask):
        if self.client is not None:
            app.logger.error("Attempted reinitialization of OpenTokClient")
            return
        try:
            api_key = app.config["VONAGE_API_KEY"]
            api_secret = app.config["VONAGE_API_SECRET"]
        except Exception:
            raise Exception("You must define API_KEY and API_SECRET in app config")

        self.client = Client(api_key, api_secret)

    def create_session(self) -> Session:
        self._require_init()
        return self.client.create_session()

    def create_host_token(self, session_id: str, user: Users) -> str:
        self._require_init()
        return self.create_token(
            session_id, Roles.moderator, self.create_user_metadata(user)
        )

    def create_guest_token(self, session_id: str, user: Users) -> str:
        self._require_init()
        return self.create_token(
            session_id, Roles.moderator, self.create_user_metadata(user)
        )

    def create_user_metadata(self, user: Users) -> dict:
        self._require_init()
        return json.dumps({"name": user.display_name})

    def create_token(self, session_id: str, role: Roles, metadata: dict) -> str:
        self._require_init()
        return self.client.generate_token(
            session_id=session_id, role=role, data=metadata
        )
