from __future__ import annotations

from unittest.mock import patch

from api.constants import V1_API_PREFIX
from models.symptom import Symptom
from tests.functional.conftest import (
    admin_user_email,
    patient_user_email,
    provider_user_email,
)

base_url = f"{V1_API_PREFIX}/health/symptoms"


class TestGetSymptomList:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_get_symptoms_as_provider(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        symptoms,
        provider_user,
        patient_user,
    ):
        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 3
        assert data["next"] is None
        assert data["previous"] is None
        for i in range(0, len(symptoms)):
            result = data["results"][i]
            actual = symptoms[i]
            assert result["id"] == actual.id
            assert result["description"] == actual.description
            assert result["name"] == actual.name
            assert result["updated_at"] == actual.updated_at.isoformat()
            assert result["created_at"] == actual.created_at.isoformat()

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
        symptoms,
        provider_user,
        patient_user,
    ):
        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 3
        assert data["next"] is None
        assert data["previous"] is None
        for i in range(0, len(symptoms)):
            result = data["results"][i]
            actual = symptoms[i]
            assert result["id"] == actual.id
            assert result["description"] == actual.description
            assert result["name"] == actual.name
            assert result["updated_at"] == actual.updated_at.isoformat()
            assert result["created_at"] == actual.created_at.isoformat()

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_get_symptoms_as_admin(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        symptoms,
        provider_user,
        patient_user,
    ):
        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 3
        assert data["next"] is None
        assert data["previous"] is None
        for i in range(0, len(symptoms)):
            result = data["results"][i]
            actual = symptoms[i]
            assert result["id"] == actual.id
            assert result["description"] == actual.description
            assert result["name"] == actual.name
            assert result["updated_at"] == actual.updated_at.isoformat()
            assert result["created_at"] == actual.created_at.isoformat()

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": provider_user_email},
    )
    def test_create_symptom_as_provider(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        symptoms,
        provider_user,
    ):
        json_body = {
            "name": "Insomnia",
            "description": "Persistent problems falling and staying asleep",
        }
        response = test_client.post(
            f"{base_url}/", headers={"Authorization": "test"}, json=json_body
        )

        assert response.status_code == 401
        assert "Only admins can perform this action" in response.text

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_create_symptom_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        symptoms,
        patient_user,
    ):
        json_body = {
            "name": "Insomnia",
            "description": "Persistent problems falling and staying asleep",
        }
        response = test_client.post(
            f"{base_url}/", headers={"Authorization": "test"}, json=json_body
        )

        assert response.status_code == 401
        assert "Only admins can perform this action" in response.text

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_create_symptom_as_admin(
        self,
        get_token_mock,
        decode_token_mock,
        test_client,
        database,
        symptoms,
        admin_user,
    ):
        json_body = {
            "name": "Insomnia",
            "description": "Persistent problems falling and staying asleep",
        }
        response = test_client.post(
            f"{base_url}/", headers={"Authorization": "test"}, json=json_body
        )

        assert response.status_code == 201
        result = response.get_json()

        assert result["description"] == json_body["description"]
        assert result["name"] == json_body["name"]

        created_symptom = database.session.get(Symptom, result["id"])
        assert result["id"] == created_symptom.id
        assert result["description"] == created_symptom.description
        assert result["name"] == created_symptom.name
        assert result["updated_at"] == created_symptom.updated_at.isoformat()
        assert result["created_at"] == created_symptom.created_at.isoformat()
