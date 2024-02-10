from __future__ import annotations

from unittest.mock import patch

from api.constants import V1_API_PREFIX
from models.admin_profile import AdminProfile
from tests.functional.conftest import (
    admin_user_email,
    patient_user2_email,
    patient_user_email,
    provider_user2_email,
    provider_user_email,
)

base_url = f"{V1_API_PREFIX}/appointments"


def verify_call_participant_data(json_data, user):
    assert json_data["display_name"] == user.display_name
    assert json_data["photo"] == ""


def verify_appointments_legacy_json(
    json_data, appointment, provider_user, patient_user
):
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


class TestGetAppointmentList:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_get_user_appointments_as_provider(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        provider_user,
        patient_user,
    ):
        appointments = [
            booked_vonage_appointment,
            booked_appointment_in_two_weeks,
            booked_appointment_in_four_weeks,
            booked_appointment_in_four_weeks_1_2,
        ]
        appointments.sort(key=lambda x: x.start_time)

        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["count"] == len(appointments)
        assert json_data["next"] is None
        assert json_data["previous"] is None
        for i in range(len(appointments)):
            verify_appointments_legacy_json(
                json_data["results"][i], appointments[i], provider_user, patient_user
            )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_user_appointments_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        test_client,
        provider_user,
        patient_user,
    ):
        appointments = [
            booked_vonage_appointment,
            booked_appointment_in_two_weeks,
            booked_appointment_in_four_weeks,
        ]
        appointments.sort(key=lambda x: x.start_time)

        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()

        print(json_data)
        assert json_data["count"] == len(appointments)
        assert json_data["next"] is None
        assert json_data["previous"] is None
        for i in range(len(appointments)):
            verify_appointments_legacy_json(
                json_data["results"][i], appointments[i], provider_user, patient_user
            )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_user_appointments_as_admin_and_patient(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        database,
        test_client,
        provider_user,
        patient_user,
    ):
        admin = AdminProfile(user_id=patient_user.id, active=True)
        database.session.add(admin)
        database.session.commit()
        appointments = [
            booked_vonage_appointment,
            booked_appointment_in_two_weeks,
            booked_appointment_in_four_weeks,
        ]
        appointments.sort(key=lambda x: x.start_time)

        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["count"] == len(appointments)
        assert json_data["next"] is None
        assert json_data["previous"] is None
        for i in range(len(appointments)):
            verify_appointments_legacy_json(
                json_data["results"][i], appointments[i], provider_user, patient_user
            )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_get_user_appointments_as_admin_and_provider(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        test_client,
        database,
        provider_user,
        patient_user,
    ):
        admin = AdminProfile(user_id=provider_user.id, active=True)
        database.session.add(admin)
        database.session.commit()
        appointments = [
            booked_vonage_appointment,
            booked_appointment_in_two_weeks,
            booked_appointment_in_four_weeks,
            booked_appointment_in_four_weeks_1_2,
        ]
        appointments.sort(key=lambda x: x.start_time)

        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["count"] == len(appointments)
        assert json_data["next"] is None
        assert json_data["previous"] is None
        for i in range(len(appointments)):
            verify_appointments_legacy_json(
                json_data["results"][i], appointments[i], provider_user, patient_user
            )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_get_user_appointments_as_admin_only(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        test_client,
        provider_user,
        patient_user,
        admin_user,
    ):
        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        print(json_data)
        assert json_data["count"] == 0
        assert json_data["next"] is None
        assert json_data["previous"] is None
        assert len(json_data["results"]) == 0

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_all_appointments_as_admin_and_patient(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        database,
        test_client,
        provider_user,
        patient_user,
    ):
        admin = AdminProfile(user_id=patient_user.id, active=True)
        database.session.add(admin)
        database.session.commit()
        appointments = [
            booked_vonage_appointment,
            booked_appointment_in_two_weeks,
            booked_appointment_in_four_weeks,
            booked_appointment_in_two_weeks_2_2,
            booked_appointment_in_four_weeks_1_2,
            canceled_appointment_in_one_week,
        ]
        appointments.sort(key=lambda x: x.start_time)

        response = test_client.get(
            f"{base_url}/?all=true",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        print(json_data)
        assert json_data["count"] == len(appointments)
        assert json_data["next"] is None
        assert json_data["previous"] is None
        for i in range(len(appointments)):
            verify_appointments_legacy_json(
                json_data["results"][i], appointments[i], provider_user, patient_user
            )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_get_all_appointments_as_admin_and_provider(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        test_client,
        database,
        provider_user,
        patient_user,
    ):
        admin = AdminProfile(user_id=provider_user.id, active=True)
        database.session.add(admin)
        database.session.commit()
        appointments = [
            booked_vonage_appointment,
            booked_appointment_in_two_weeks,
            booked_appointment_in_four_weeks,
            booked_appointment_in_two_weeks_2_2,
            booked_appointment_in_four_weeks_1_2,
            canceled_appointment_in_one_week,
        ]
        appointments.sort(key=lambda x: x.start_time)

        response = test_client.get(
            f"{base_url}/?all=true",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["count"] == len(appointments)
        assert json_data["next"] is None
        assert json_data["previous"] is None
        for i in range(len(appointments)):
            verify_appointments_legacy_json(
                json_data["results"][i], appointments[i], provider_user, patient_user
            )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_get_all_appointments_as_admin_only(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        test_client,
        provider_user,
        patient_user,
        admin_user,
    ):
        appointments = [
            booked_vonage_appointment,
            booked_appointment_in_two_weeks,
            booked_appointment_in_four_weeks,
            booked_appointment_in_two_weeks_2_2,
            booked_appointment_in_four_weeks_1_2,
            canceled_appointment_in_one_week,
        ]
        appointments.sort(key=lambda x: x.start_time)

        response = test_client.get(
            f"{base_url}/?all=true",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["count"] == len(appointments)
        assert json_data["next"] is None
        assert json_data["previous"] is None
        for i in range(len(appointments)):
            verify_appointments_legacy_json(
                json_data["results"][i], appointments[i], provider_user, patient_user
            )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user2_email},
    )
    def test_get_user_appointments_as_provider2(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        test_client,
        provider_user,
        patient_user,
        provider_user2,
    ):
        appointments = [booked_appointment_in_two_weeks_2_2]
        appointments.sort(key=lambda x: x.start_time)

        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["count"] == len(appointments)
        assert json_data["next"] is None
        assert json_data["previous"] is None
        for i in range(len(appointments)):
            verify_appointments_legacy_json(
                json_data["results"][i], appointments[i], provider_user, patient_user
            )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user2_email},
    )
    def test_get_user_appointments_as_patient_2(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_two_weeks_2_2,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        test_client,
        provider_user,
        patient_user,
        patient_user2,
    ):
        appointments = [
            booked_appointment_in_two_weeks_2_2,
            booked_appointment_in_four_weeks_1_2,
        ]
        appointments.sort(key=lambda x: x.start_time)

        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["count"] == len(appointments)
        assert json_data["next"] is None
        assert json_data["previous"] is None
        for i in range(len(appointments)):
            verify_appointments_legacy_json(
                json_data["results"][i], appointments[i], provider_user, patient_user
            )

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user2_email},
    )
    def test_get_user_appointments_as_provider_no_apointments(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        booked_appointment_in_four_weeks_1_2,
        canceled_appointment_in_one_week,
        test_client,
        provider_user,
        patient_user,
        provider_user2,
    ):
        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["count"] == 0
        assert json_data["next"] is None
        assert json_data["previous"] is None
        assert len(json_data["results"]) == 0

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user2_email},
    )
    def test_get_user_appointments_as_patient_not_on_appointments(
        self,
        get_token_mock,
        decode_token_mock,
        booked_vonage_appointment,
        booked_appointment_in_two_weeks,
        booked_appointment_in_four_weeks,
        canceled_appointment_in_one_week,
        test_client,
        provider_user,
        patient_user,
        patient_user2,
    ):
        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["count"] == 0
        assert json_data["next"] is None
        assert json_data["previous"] is None
        assert len(json_data["results"]) == 0
