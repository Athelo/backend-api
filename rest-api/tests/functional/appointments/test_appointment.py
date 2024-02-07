from __future__ import annotations

from unittest.mock import patch

from api.constants import V1_API_PREFIX
from flask.testing import FlaskClient
from models.appointments.appointment import Appointment
from tests.functional.conftest import (
    admin_user_email,
    patient_user_email,
    provider_user_email,
)

base_url = f"{V1_API_PREFIX}/appointment"


def verify_call_participant_data(json_data, user):
    assert json_data["display_name"] == user.display_name
    assert json_data["photo"] == ""


def verify_appointment_legacy_json(json_data, appointment, provider_user, patient_user):
    assert json_data["id"] == appointment.id
    verify_call_participant_data(json_data["patient"], patient_user)
    verify_call_participant_data(json_data["provider"], provider_user)
    assert json_data["start_time"] == appointment.start_time.isoformat()
    assert json_data["end_time"] == appointment.end_time.isoformat()
    if appointment.zoom_meeting:
        assert json_data["zoom_host_url"] == appointment.zoom_meeting.zoom_host_url
        assert json_data["zoom_join_url"] == appointment.zoom_meeting.zoom_join_url
    else:
        assert json_data["zoom_host_url"] == ""
        assert json_data["zoom_join_url"] == ""

    if appointment.vonage_session:
        assert json_data["vonage_session"] == appointment.vonage_session.session_id
    else:
        assert json_data["vonage_session"] == ""


class TestGetAppointmentDetail:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_get_appointment_as_provider(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        booked_vonage_appointment,
        provider_user,
        patient_user,
    ):
        appointment = booked_vonage_appointment
        response = test_client.get(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        verify_appointment_legacy_json(
            response.get_json(), appointment, provider_user, patient_user
        )
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_appointment_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_appointment_as_admin_and_patient(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_appointment_as_admin_and_provider(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_appointment_as_admin_only(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_appointment_as_provider_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_appointment_as_patient_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False


class TestDeleteAppointmentDetail:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_delete_appointment_as_provider(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_delete_appointment_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_delete_appointment_as_admin_and_patient(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_delete_appointment_as_admin_and_provider(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_delete_appointment_as_admin_only(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_delete_appointment_as_provider_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_delete_appointment_as_patient_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False


class TestGetAppointmentVonageDetail:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_video_call_detail_as_provider(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_video_call_detail_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_video_call_detail_as_admin_and_patient(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_video_call_detail_as_admin_and_provider(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_video_call_detail_as_admin_only(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_video_call_detail_as_provider_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_video_call_detail_as_patient_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        database,
        booked_vonage_appointment,
    ):
        assert False


class OldTests:
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
