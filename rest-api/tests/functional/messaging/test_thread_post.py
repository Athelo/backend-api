from __future__ import annotations

from unittest.mock import patch

import pytest
from api.constants import V1_API_PREFIX
from flask.testing import FlaskClient
from models.thread_post import ThreadPost
from tests.functional.conftest import patient_user2_email, patient_user_email
from tests.functional.messaging.conftest import (
    add_user_to_thread,
    create_community_thread,
    thread_name_list,
)

base_url = f"{V1_API_PREFIX}/community-threads"


def add_messages_to_thread(
    thread,
    author,
    database,
    content="test",
):
    post = ThreadPost(thread_id=thread.id, author_id=author.id, content=content)
    database.session.add(post)
    database.session.commit()
    return post


@pytest.fixture
def community_thread_with_messages(admin_user, patient_user, provider_user, database):
    thread = create_community_thread(admin_user.admin_profile, thread_name_list[0])
    add_user_to_thread(patient_user, thread, database)
    add_user_to_thread(provider_user, thread, database)

    add_messages_to_thread(thread, admin_user, database, "Hello, all")
    add_messages_to_thread(
        thread, patient_user, database, f"Hello! I'm {patient_user.display_name}"
    )
    add_messages_to_thread(
        thread, provider_user, database, f"Hello. I am {provider_user.display_name}"
    )
    add_messages_to_thread(thread, admin_user, database, "Hello, all")
    return thread


class TestThreadPost:
    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_get_posts(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_thread_with_messages,
        database,
    ):
        thread = community_thread_with_messages
        response = test_client.get(
            f"{base_url}/{thread.id}/posts/",
            headers={"Authorization": "test"},
        )

        response_data = response.get_json()
        results = response_data["results"]
        assert response.status_code == 200
        assert response_data["count"] == len(thread.posts)

        for i in range(len(thread.posts)):
            print(results[i])
            assert results[i]["id"] == thread.posts[i].id
            assert results[i]["author_id"] == thread.posts[i].author_id
            assert results[i]["content"] == thread.posts[i].content
            assert results[i]["created_at"] == thread.posts[i].created_at.isoformat()
            assert results[i]["updated_at"] == thread.posts[i].updated_at.isoformat()
            assert results[i]["thread_id"] == thread.posts[i].thread_id

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user_email},
    )
    def test_add_post(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_thread_with_messages,
        patient_user,
        database,
    ):
        thread = community_thread_with_messages
        json_data = {"content": "New message"}
        response = test_client.put(
            f"{base_url}/{thread.id}/posts/",
            headers={"Authorization": "test"},
            json=json_data,
        )
        result = response.get_json()
        assert response.status_code == 201
        assert result["author_id"] == patient_user.id
        assert result["thread_id"] == thread.id
        assert result["content"] == json_data["content"]
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result

    @patch("auth.middleware.get_token", autospec=True, return_value="foo")
    @patch(
        "auth.middleware.decode_token",
        autospec=True,
        return_value={"uid": "foo", "email": patient_user2_email},
    )
    def test_add_post_not_joined(
        self,
        get_token_mock,
        decode_token_mock,
        test_client: FlaskClient,
        community_thread_with_messages,
        patient_user2,
        database,
    ):
        thread = community_thread_with_messages
        json_data = {"content": "New message"}
        response = test_client.put(
            f"{base_url}/{thread.id}/posts/",
            headers={"Authorization": "test"},
            json=json_data,
        )
        assert response.status_code == 401
        assert (
            "Cannot post to a group messagee that you haven&#39;t joined"
            in response.text
        )
