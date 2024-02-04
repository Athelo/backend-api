from __future__ import annotations

from unittest.mock import patch

from api.constants import V1_API_PREFIX
from flask.testing import FlaskClient


class TestMainApi:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": "test@test.foo"},
    )
    def test_protected_valid_token(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        booked_appointment_in_one_week,
        database,
    ):
        response = test_client.get(
            f"{V1_API_PREFIX}/appointment/{booked_appointment_in_one_week.id}/",
        )

        assert response.status_code == 200
