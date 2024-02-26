from __future__ import annotations

from unittest.mock import patch

from api.constants import V1_API_PREFIX
from models.admin_profile import AdminProfile
from models.appointments.appointment import AppointmentStatus
from tests.functional.conftest import (
    admin_user_email,
    patient_user2_email,
    patient_user_email,
    provider_user2_email,
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
        assert json_data["zoom_host_url"] is None
        assert json_data["zoom_join_url"] is None

    if appointment.vonage_session:
        assert json_data["vonage_session"] == appointment.vonage_session.session_id
    else:
        assert json_data["vonage_session"] is None


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
        booked_vonage_appointment,
        test_client,
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
        booked_vonage_appointment,
        database,
        test_client,
        provider_user,
        patient_user,
    ):
        admin = AdminProfile(user_id=patient_user.id, active=True)
        database.session.add(admin)
        database.session.commit()
        appointment = booked_vonage_appointment
        response = test_client.get(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        verify_appointment_legacy_json(
            response.get_json(), appointment, provider_user, patient_user
        )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_get_appointment_as_admin_and_provider(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        database,
        provider_user,
        patient_user,
    ):
        admin = AdminProfile(user_id=provider_user.id, active=True)
        database.session.add(admin)
        database.session.commit()
        appointment = booked_vonage_appointment
        response = test_client.get(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        verify_appointment_legacy_json(
            response.get_json(), appointment, provider_user, patient_user
        )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_get_appointment_as_admin_only(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
        admin_user,
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

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user2_email},
    )
    def test_get_appointment_as_provider_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
        provider_user2,
    ):
        appointment = booked_vonage_appointment
        response = test_client.get(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 401
        assert (
            "Appointment does not exist or the user does not have permissions to view it"
            in response.text
        )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user2_email},
    )
    def test_get_appointment_as_patient_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
        patient_user2,
    ):
        appointment = booked_vonage_appointment
        response = test_client.get(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )
        print(response.text)
        assert response.status_code == 401
        assert (
            "Appointment does not exist or the user does not have permissions to view it"
            in response.text
        )


class TestDeleteAppointmentDetail:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_delete_appointment_as_provider(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
    ):
        appointment = booked_vonage_appointment
        response = test_client.delete(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 204
        assert response.text == ""
        assert appointment.status == AppointmentStatus.CANCELLED

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
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
    ):
        appointment = booked_vonage_appointment
        response = test_client.delete(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 204
        assert response.text == ""
        assert appointment.status == AppointmentStatus.CANCELLED

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
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
        database,
    ):
        admin = AdminProfile(user_id=patient_user.id, active=True)
        database.session.add(admin)
        database.session.commit()
        appointment = booked_vonage_appointment
        response = test_client.delete(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 204
        assert response.text == ""
        assert appointment.status == AppointmentStatus.CANCELLED

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_delete_appointment_as_admin_and_provider(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
        database,
    ):
        admin = AdminProfile(user_id=provider_user.id, active=True)
        database.session.add(admin)
        database.session.commit()
        appointment = booked_vonage_appointment
        response = test_client.delete(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 204
        assert response.text == ""
        assert appointment.status == AppointmentStatus.CANCELLED

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_delete_appointment_as_admin_only(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
        admin_user,
    ):
        appointment = booked_vonage_appointment
        response = test_client.delete(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 204
        assert response.text == ""
        assert appointment.status == AppointmentStatus.CANCELLED

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user2_email},
    )
    def test_delete_appointment_as_provider_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
        provider_user2,
    ):
        appointment = booked_vonage_appointment
        response = test_client.delete(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 401
        assert (
            "Appointment does not exist or the user does not have permissions to delete it"
            in response.text
        )
        assert appointment.status == AppointmentStatus.BOOKED

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user2_email},
    )
    def test_delete_appointment_as_patient_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
        patient_user2,
    ):
        appointment = booked_vonage_appointment
        response = test_client.delete(
            f"{base_url}/{appointment.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 401
        assert (
            "Appointment does not exist or the user does not have permissions to delete it"
            in response.text
        )
        assert appointment.status == AppointmentStatus.BOOKED


class TestGetAppointmentVonageDetail:
    PATCH_BASE_URL = "services.opentok.OpenTokClient"

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_get_token_as_provider(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
    ):
        appointment = booked_vonage_appointment
        expected_token = "token"
        with patch(
            f"{self.PATCH_BASE_URL}.create_host_token", return_value=expected_token
        ):
            response = test_client.get(
                f"{base_url}/{appointment.id}/vonage-appointment-details/",
                headers={"Authorization": "test"},
            )

        assert response.status_code == 200
        assert response.get_json()["token"] == expected_token

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_token_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
    ):
        appointment = booked_vonage_appointment
        expected_token = "token"
        with patch(
            f"{self.PATCH_BASE_URL}.create_guest_token", return_value=expected_token
        ):
            response = test_client.get(
                f"{base_url}/{appointment.id}/vonage-appointment-details/",
                headers={"Authorization": "test"},
            )

        assert response.status_code == 200
        assert response.get_json()["token"] == expected_token

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_token_as_admin_and_patient(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
    ):
        appointment = booked_vonage_appointment
        expected_token = "token"
        with patch(
            f"{self.PATCH_BASE_URL}.create_guest_token", return_value=expected_token
        ):
            response = test_client.get(
                f"{base_url}/{appointment.id}/vonage-appointment-details/",
                headers={"Authorization": "test"},
            )

        assert response.status_code == 200
        assert response.get_json()["token"] == expected_token

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_get_token_as_admin_and_provider(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user,
        patient_user,
    ):
        appointment = booked_vonage_appointment
        expected_token = "token"
        with patch(
            f"{self.PATCH_BASE_URL}.create_host_token", return_value=expected_token
        ):
            response = test_client.get(
                f"{base_url}/{appointment.id}/vonage-appointment-details/",
                headers={"Authorization": "test"},
            )

        assert response.status_code == 200
        assert response.get_json()["token"] == expected_token

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_get_token_as_admin_only(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        admin_user,
    ):
        appointment = booked_vonage_appointment
        expected_token = "token"
        with patch(
            f"{self.PATCH_BASE_URL}.create_host_token", return_value=expected_token
        ):
            response = test_client.get(
                f"{base_url}/{appointment.id}/vonage-appointment-details/",
                headers={"Authorization": "test"},
            )

        print(response.text)
        assert response.status_code == 200
        assert response.get_json()["token"] == expected_token

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user2_email},
    )
    def test_get_token_as_provider_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        provider_user2,
    ):
        appointment = booked_vonage_appointment
        expected_token = "token"
        with patch(
            f"{self.PATCH_BASE_URL}.create_guest_token", return_value=expected_token
        ):
            response = test_client.get(
                f"{base_url}/{appointment.id}/vonage-appointment-details/",
                headers={"Authorization": "test"},
            )
        assert response.status_code == 401
        assert (
            "Appointment does not exist or the user does not have permissions to view it"
            in response.text
        )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user2_email},
    )
    def test_get_token_as_patient_not_on_appointment(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        test_client,
        patient_user2,
    ):
        appointment = booked_vonage_appointment
        expected_token = "token"
        with patch(
            f"{self.PATCH_BASE_URL}.create_guest_token", return_value=expected_token
        ):
            response = test_client.get(
                f"{base_url}/{appointment.id}/vonage-appointment-details/",
                headers={"Authorization": "test"},
            )

        assert response.status_code == 401
        assert (
            "Appointment does not exist or the user does not have permissions to view it"
            in response.text
        )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_get_token_on_appointment_without_vonage_session(
        self,
        get_token_mock,
        decode_token_mock,
        booked_appointment_in_one_week,
        test_client,
        provider_user,
        patient_user,
    ):
        appointment = booked_appointment_in_one_week
        expected_token = "token"
        with patch(
            f"{self.PATCH_BASE_URL}.create_guest_token", return_value=expected_token
        ):
            response = test_client.get(
                f"{base_url}/{appointment.id}/vonage-appointment-details/",
                headers={"Authorization": "test"},
            )

        assert response.status_code == 422
        assert (
            f"Appointment {appointment.id} isn&#39;t conducted through vonage"
            in response.text
        )
