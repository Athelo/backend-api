from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from api.constants import V1_API_PREFIX
from api.tests.conftest import admin_user_email, patient_user_email
from flask.testing import FlaskClient
from models.community_thread import CommunityThread
from models.users import Users

thread_name_list = ["Remission", "Fertility", "Diet"]


def create_community_thread(owner, name):
    thread = CommunityThread(display_name=name, owner_id=owner.id, description="")
    return thread


@pytest.fixture
def community_threads(database, admin_user):
    threads = []
    for name in thread_name_list:
        thread = create_community_thread(admin_user.admin_profile, name)
        database.session.add(thread)
        threads.append(thread)
    database.session.commit()
    return threads


def add_user_to_thread(user: Users, thread: CommunityThread, database):
    thread.participants.append(user)
    database.session.add(thread)
    database.session.commit()


class TestCommunityThread:
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
            f"{V1_API_PREFIX}/chats/group-conversations/",
            headers={"Authorization": "test"},
        )

        result = response.get_json()
        print(response.text)
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
            f"{V1_API_PREFIX}/chats/group-conversations/",
            headers={"Authorization": "test"},
        )

        result = response.get_json()
        print(response.text)
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
            f"{V1_API_PREFIX}/chats/group-conversations/",
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
            f"{V1_API_PREFIX}/chats/group-conversations/",
            headers={"Authorization": "test"},
            json=data,
        )

        result = response.get_json()
        assert response.status_code == 201
        assert result["active"]
        assert result["created_at"][:-4] == result["updated_at"][:-4]
        assert result["owner"] == admin_user.admin_profile.id
        assert len(result["participants"])
        assert admin_user.id in result["participants"]
        assert len(result["posts"]) == 0
        assert result["description"] == data["description"]
