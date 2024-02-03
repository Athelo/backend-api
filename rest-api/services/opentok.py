import json

from flask import Flask
from models.users import Users
from opentok import Client, Roles, Session


class OpenTokClient(object):
    _instance = None
    client = None

    def __init__(self):
        raise Exception(
            "call init_app(app) to initialize or instance() to get instance"
        )

    @classmethod
    def instance(cls):
        if cls._instance is None:
            raise Exception("Class has not been initialized")
        return cls._instance

    @classmethod
    def init_app(cls, app: Flask):
        if cls._instance is not None:
            app.logger.error("Attempted reinitialization of singlton OpenTokClient")
            return
        cls._instance = cls.__new__(cls)
        try:
            api_key = app.config["VONAGE_API_KEY"]
            api_secret = app.config["VONAGE_API_SECRET"]
        except Exception:
            raise Exception("You must define API_KEY and API_SECRET in app config")
        cls.client = Client(api_key, api_secret)

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
