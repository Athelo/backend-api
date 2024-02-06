from __future__ import annotations

import json
from unittest.mock import patch

from flask.testing import FlaskClient
from models.community_thread import CommunityThread
from schemas.user_profile import UserProfileSchema

from api.constants import V1_API_PREFIX
from api.tests.conftest import admin_user_email, patient_user_email
from api.tests.messaging.conftest import add_user_to_thread

base_url = f"{V1_API_PREFIX}/chats/group-conversations"


class TestCommunityThreadList:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_threads_none_joined(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        result = response.get_json()
        assert response.status_code == 200
        assert len(result["results"]) == len(community_threads)
        for thread_json in result["results"]:
            assert not thread_json["belong_to"]

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_threads_one_joined(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        joined_thread = community_threads[0]

        add_user_to_thread(patient_user, joined_thread, database)
        response = test_client.get(
            f"{base_url}/",
            headers={"Authorization": "test"},
        )

        result = response.get_json()
        assert response.status_code == 200
        assert len(result["results"]) == len(community_threads)
        for thread_json in result["results"]:
            if thread_json["id"] == joined_thread.id:
                assert thread_json["belong_to"]
            else:
                assert not thread_json["belong_to"]

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_create_thread_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        data = {"display_name": "Family Planning", "description": ""}
        response = test_client.put(
            f"{base_url}/",
            headers={"Authorization": "test"},
            json=json.dumps(data),
        )

        assert response.status_code == 401
        assert "Only admins can perform this action" in response.text

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_create_thread_as_admin(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        data = {"display_name": "Family Planning", "description": ""}
        response = test_client.put(
            f"{base_url}/",
            headers={"Authorization": "test"},
            json=data,
        )

        result = response.get_json()
        assert response.status_code == 201
        assert result["active"]
        assert result["created_at"][:-4] == result["updated_at"][:-4]
        assert result["owner"] == admin_user.admin_profile.id
        assert len(result["participants"]) == 1
        assert admin_user.id in result["participants"]
        assert len(result["posts"]) == 0
        assert result["description"] == data["description"]

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_update_thread_as_admin(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        thread = community_threads[0]
        new_name = f"{thread.display_name} New"
        new_description = f"{thread.description} New"
        data = {"display_name": new_name, "description": new_description}
        response = test_client.post(
            f"{base_url}/{thread.id}/",
            headers={"Authorization": "test"},
            json=data,
        )

        result = response.get_json()
        assert response.status_code == 202
        assert result["display_name"] == data["display_name"]
        assert result["active"]
        assert result["owner"] == admin_user.admin_profile.id
        assert len(result["participants"]) == 1
        assert admin_user.id in result["participants"]
        assert len(result["posts"]) == 0
        assert result["description"] == data["description"]

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_update_thread_as_patient(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        thread = community_threads[0]
        new_name = f"{thread.display_name} New"
        new_description = f"{thread.description} New"
        data = {"display_name": new_name, "description": new_description}
        response = test_client.post(
            f"{base_url}/{thread.id}/",
            headers={"Authorization": "test"},
            json=data,
        )

        assert response.status_code == 401
        assert "Only admins can perform this action" in response.text


class TestCommunityThreadDetail:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_get_thread_detail_joined(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        thread: CommunityThread = community_threads[2]
        response = test_client.get(
            f"{base_url}/{thread.id}/",
            headers={"Authorization": "test"},
        )

        result = response.get_json()
        assert response.status_code == 200
        assert result["belong_to"]
        assert result["name"] == thread.display_name
        assert result["owner"] == UserProfileSchema().dump(thread.owner.user)
        assert len(result["user_profiles"]) == 1
        assert admin_user.id in [user["id"] for user in result["user_profiles"]]
        assert result["chat_room_type"] == 2
        assert result["is_public"]
        assert result["user_profiles_count"] == len(thread.participants)
        assert result["chat_room_identifier"] == thread.id

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_thread_detail_not_joined(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        thread = community_threads[2]
        response = test_client.get(
            f"{base_url}/{thread.id}/",
            headers={"Authorization": "test"},
        )

        result = response.get_json()
        assert response.status_code == 200
        assert not result["belong_to"]
        assert result["name"] == thread.display_name
        assert result["owner"] == UserProfileSchema().dump(thread.owner.user)
        assert len(result["user_profiles"]) == 1
        assert admin_user.id in [user["id"] for user in result["user_profiles"]]
        assert result["chat_room_type"] == 2
        assert result["is_public"]
        assert result["user_profiles_count"] == len(thread.participants)
        assert result["chat_room_identifier"] == thread.id

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_join_thread(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        thread = community_threads[1]
        response = test_client.put(
            f"{base_url}/{thread.id}/join/",
            headers={"Authorization": "test"},
        )
        assert response.status_code == 202
        assert response.text == ""

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_join_thread_already_member(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        thread = community_threads[1]

        response = test_client.put(
            f"{base_url}/{thread.id}/join/",
            headers={"Authorization": "test"},
        )
        assert response.status_code == 409
        assert f"User {admin_user.id} is already in thread {thread.id}" in response.text

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_leave_thread(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        thread = community_threads[1]
        thread.participants.append(patient_user)
        database.session.add(thread)
        database.session.commit()

        response = test_client.put(
            f"{base_url}/{thread.id}/leave/",
            headers={"Authorization": "test"},
        )
        assert response.status_code == 202
        assert response.text == ""

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": admin_user_email},
    )
    def test_leave_thread_as_owner(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        thread = community_threads[1]

        response = test_client.put(
            f"{base_url}/{thread.id}/leave/",
            headers={"Authorization": "test"},
        )
        assert response.status_code == 409
        assert "Thread owner cannot leave thread" in response.text

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_leave_thread_not_joined(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_threads,
        admin_user,
        patient_user,
        database,
    ):
        thread = community_threads[2]
        response = test_client.put(
            f"{base_url}/{thread.id}/leave/",
            headers={"Authorization": "test"},
        )
        assert response.status_code == 409
        assert f"User {patient_user.id} is not in thread {thread.id}" in response.text
