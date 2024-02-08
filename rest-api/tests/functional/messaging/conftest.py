from __future__ import annotations

import pytest
from models.community_thread import CommunityThread
from models.users import Users

thread_name_list = ["Remission", "Fertility", "Diet"]


def create_community_thread(owner, name):
    thread = CommunityThread(
        display_name=name, owner_id=owner.id, description=f"{name} description"
    )
    thread.participants.append(owner.user)
    return thread


@pytest.fixture
def community_threads(database, admin_user):
    threads = []
    for name in thread_name_list:
        thread = create_community_thread(admin_user.admin_profile, name)
        database.session.add(thread)
        threads.append(thread)

    database.session.commit()
    return database.session.query(CommunityThread).all()


def add_user_to_thread(user: Users, thread: CommunityThread, database):
    thread.participants.append(user)
    database.session.add(thread)
    database.session.commit()
