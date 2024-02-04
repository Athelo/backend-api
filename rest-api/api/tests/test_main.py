from __future__ import annotations

from unittest.mock import patch

from flask.testing import FlaskClient


class TestMainApi:
    def test_public(self, test_client: FlaskClient, database):
        response = test_client.get(
            "public/",
        )
        assert response.status_code == 200
        assert "This is Athelo Health's API, and it is" in response.text

    def test_proteected_unauthenticated(self, test_client: FlaskClient, database):
        response = test_client.get(
            "protected/",
        )
        assert response.status_code == 401

    def test_protected_invalid_token(self, test_client: FlaskClient, database):
        response = test_client.get("protected/", headers={"Authorization": "test"})
        assert response.status_code == 403
        assert "Error with authentication: malformed header." == response.text

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": "test@test.foo"},
    )
    def test_protected_valid_token(
        self, get_token_mock, decode_token_mock, test_client: FlaskClient, database
    ):
        response = test_client.get("protected/", headers={"Authorization": "test"})
        assert response.status_code == 200
        assert False
