from __future__ import annotations

import html
from datetime import date, timedelta
from unittest.mock import patch

from api.constants import DATE_FORMAT, V1_API_PREFIX
from models.users import Users
from tests.functional.conftest import patient_user2_email, patient_user_email

base_url = f"{V1_API_PREFIX}/health/user_symptoms"


class TestGetUserSymptomDetail:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_symptom_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        patient_user_with_symptoms: Users,
    ):
        symptom = patient_user_with_symptoms.patient_symptoms[-1]
        response = test_client.get(
            f"{base_url}/{symptom.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["id"] == symptom.id
        assert data["symptom"]["id"] == symptom.symptom.id
        assert data["symptom"]["name"] == symptom.symptom.name
        assert data["symptom"]["created_at"] == symptom.symptom.created_at.isoformat()
        assert data["symptom"]["updated_at"] == symptom.symptom.updated_at.isoformat()
        assert data["note"] == symptom.note
        assert data["occurrence_date"] == symptom.occurrence_date.isoformat()

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_symptom_as_patient_no_symptom(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        patient_user,
    ):
        response = test_client.get(
            f"{base_url}/{5}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 404
        assert response.get_json() == {
            "message": "Symptom is not accessible or does not exist"
        }

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user2_email},
    )
    def test_get_symptom_as_other_patient(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        patient_user_with_symptoms,
        patient_user2,
    ):
        symptom = patient_user_with_symptoms.patient_symptoms[-1]
        response = test_client.get(
            f"{base_url}/{symptom.id}/",
            headers={"Authorization": "test"},
        )
        print(response.text)
        assert response.status_code == 403
        assert response.get_json() == {
            "message": f"User symptom {symptom.id} does not belong to User {patient_user2.email}"
        }


class TestPutUserSymptomDetail:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_symptom_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        patient_user_with_symptoms: Users,
    ):
        symptom = patient_user_with_symptoms.patient_symptoms[-1]
        response = test_client.get(
            f"{base_url}/{symptom.id}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data["id"] == symptom.id
        assert data["symptom"]["id"] == symptom.symptom.id
        assert data["symptom"]["name"] == symptom.symptom.name
        assert data["symptom"]["created_at"] == symptom.symptom.created_at.isoformat()
        assert data["symptom"]["updated_at"] == symptom.symptom.updated_at.isoformat()
        assert data["note"] == symptom.note
        assert data["occurrence_date"] == symptom.occurrence_date.isoformat()

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_symptom_as_patient_no_symptom(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        patient_user,
    ):
        response = test_client.get(
            f"{base_url}/{5}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 404
        assert response.get_json() == {
            "message": "Symptom is not accessible or does not exist"
        }

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user2_email},
    )
    def test_get_symptom_as_other_patient(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        patient_user_with_symptoms,
        patient_user2,
    ):
        symptom = patient_user_with_symptoms.patient_symptoms[-1]
        response = test_client.get(
            f"{base_url}/{symptom.id}/",
            headers={"Authorization": "test"},
        )
        print(response.text)
        assert response.status_code == 403
        assert response.get_json() == {
            "message": f"User symptom {symptom.id} does not belong to User {patient_user2.email}"
        }


class TestDeleteUserSymptomDetail:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_log_user_symptom(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        symptoms,
        patient_user_with_symptoms,
    ):
        logged_symptom = symptoms[2]
        occurence_date = date.today() - timedelta(days=3)
        json_body = {
            "symptom_id": logged_symptom.id,
            "note": "This is a note",
            "occurrence_date": occurence_date.strftime(DATE_FORMAT),
        }
        response = test_client.post(
            f"{base_url}/", headers={"Authorization": "test"}, json=json_body
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["symptom_id"] == json_body["symptom_id"]
        assert data["note"] == json_body["note"]
        assert data["occurrence_date"] == json_body["occurrence_date"]

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_log_user_symptom_malformed_date(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        symptoms,
        patient_user_with_symptoms,
    ):
        logged_symptom = symptoms[2]
        occurence_date = date.today() - timedelta(days=3)
        print(occurence_date.isoformat())
        json_body = {
            "symptom_id": logged_symptom.id,
            "note": "This is a note",
            "occurrence_date": occurence_date.strftime("%Y/%m/%d"),
        }
        response = test_client.post(
            f"{base_url}/", headers={"Authorization": "test"}, json=json_body
        )

        assert response.status_code == 422
        text = html.unescape(response.text)
        assert 'Unable to parse "occurrence_date"' in text

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_log_user_symptom_bad_symptom_id(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        symptoms,
        patient_user_with_symptoms,
    ):
        logged_symptom = symptoms[-1]
        occurence_date = date.today() - timedelta(days=3)
        print(occurence_date.isoformat())
        json_body = {
            "symptom_id": logged_symptom.id + 1,
            "note": "This is a note",
            "occurrence_date": occurence_date.strftime(DATE_FORMAT),
        }
        response = test_client.post(
            f"{base_url}/", headers={"Authorization": "test"}, json=json_body
        )

        assert response.status_code == 422
        text = html.unescape(response.text)
        assert (
            'Cannot create db entity because insert or update on table "patient_symptoms" violates foreign key constraint "fk_patient_symptoms_symptom_id_symptoms'
            in text
        )
