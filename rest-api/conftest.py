import os

import pytest
from app import create_app, db
from sqlalchemy.orm import scoped_session, sessionmaker


@pytest.fixture(scope="session")
def test_client():
    os.environ["ENVIRONMENT"] = "test"
    test_app = create_app()
    test_client = test_app.test_client()

    with test_app.app_context():
        yield test_client


@pytest.fixture(scope="session")
def database():
    db.create_all()

    yield db

    db.drop_all()


@pytest.fixture(autouse=True)
def enable_transactional_tests(database):
    """https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites"""
    print("connect to db")
    connection = database.engine.connect()
    transaction = connection.begin()

    database.session = scoped_session(
        session_factory=sessionmaker(
            bind=connection,
            join_transaction_mode="create_savepoint",
        )
    )

    yield

    database.session.close()
    transaction.rollback()
    connection.close()
