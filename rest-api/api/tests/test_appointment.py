from __future__ import annotations

from unittest.mock import patch

from flask.testing import FlaskClient
from models.appointments.appointment import Appointment

from api.constants import V1_API_PREFIX
from api.tests.conftest import admin_user_email


class TestAppointment:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_get_appointment_detail(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        booked_appointment_in_one_week,
        admin_user,
        database,
    ):
        appointment = booked_appointment_in_one_week
        response = test_client.get(
            f"{V1_API_PREFIX}/appointment/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        result = response.get_json()
        assert response.status_code == 200
        assert result["id"] == appointment.id
        assert (
            result["provider"]["display_name"] == appointment.provider.user.display_name
        )
        assert result["provider"]["photo"] == ""
        assert (
            result["patient"]["display_name"] == appointment.patient.user.display_name
        )
        assert result["patient"]["photo"] == ""
        assert result["zoom_join_url"] is None
        assert result["zoom_host_url"] is None
        assert result["vonage_session"] is None
        assert result["start_time"] == appointment.start_time.isoformat()
        assert result["end_time"] == appointment.end_time.isoformat()

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_get_appointment_detail_not_found(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        booked_appointment_in_one_week,
        admin_user,
        database,
    ):
        appointment = booked_appointment_in_one_week
        response = test_client.get(
            f"{V1_API_PREFIX}/appointment/{appointment.id+1}/",
            headers={"Authorization": "test"},
        )
        assert response.status_code == 404
        assert "Appointment not found" in response.text

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_appointment_with_vonage_details(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        appointment_with_vonage_session: Appointment,
        admin_user,
        database,
    ):
        appointment = appointment_with_vonage_session
        response = test_client.get(
            f"{V1_API_PREFIX}/appointment/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        result = response.get_json()
        assert response.status_code == 200
        assert result["id"] == appointment.id
        assert (
            result["provider"]["display_name"] == appointment.provider.user.display_name
        )
        assert result["provider"]["photo"] == ""
        assert (
            result["patient"]["display_name"] == appointment.patient.user.display_name
        )
        assert result["patient"]["photo"] == ""
        assert result["zoom_join_url"] is None
        assert result["zoom_host_url"] is None
        assert result["vonage_session"] == appointment.vonage_session.session_id
        assert result["start_time"] == appointment.start_time.isoformat()
        assert result["end_time"] == appointment.end_time.isoformat()
