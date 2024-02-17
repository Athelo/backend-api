from __future__ import annotations

import html
from datetime import date, timedelta
from unittest.mock import patch

from api.constants import DATE_FORMAT, V1_API_PREFIX
from models.patient_symptoms import PatientSymptoms
from models.symptom import Symptom
from tests.functional.conftest import (
    patient_user_email,
)

base_url = f"{V1_API_PREFIX}/health/user_symptoms"


class TestGetSymptomList:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_symptoms_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        patient_user_with_symptoms,
    ):
        expected_symptoms: list[PatientSymptoms] = (
            database.session.query(PatientSymptoms)
            .filter_by(user_profile_id=patient_user_with_symptoms.id)
            .join(Symptom)
            .order_by(PatientSymptoms.id)
            .all()
        )

        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == len(expected_symptoms)
        assert data["next"] is None
        assert data["previous"] is None
        for i in range(0, len(expected_symptoms)):
            actual_symptom = data["results"][i]
            expected_symptom = expected_symptoms[i]
            print(actual_symptom)
            print(expected_symptom.__dict__)

            assert actual_symptom["id"] == expected_symptom.id
            assert actual_symptom["symptom"]["id"] == expected_symptom.symptom.id
            assert actual_symptom["symptom"]["name"] == expected_symptom.symptom.name
            assert (
                actual_symptom["symptom"]["created_at"]
                == expected_symptom.symptom.created_at.isoformat()
            )
            assert (
                actual_symptom["symptom"]["updated_at"]
                == expected_symptom.symptom.updated_at.isoformat()
            )
            assert actual_symptom["note"] == expected_symptom.note
            assert actual_symptom[
                "occurrence_date"
            ] == expected_symptom.occurrence_date.strftime(DATE_FORMAT)

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_symptoms_as_patient_no_symptoms_logged(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        patient_user,
    ):
        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 0
        assert data["next"] is None
        assert data["previous"] is None
        assert len(data["results"]) == 0


class TestPostUserSymptom:
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
