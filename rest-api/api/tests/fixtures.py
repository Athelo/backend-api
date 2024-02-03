import os
from datetime import datetime, timedelta

import pytest
from app import create_app, db
from models.appointments.appointment import Appointment, AppointmentStatus
from models.patient_profile import CancerStatus, PatientProfile
from models.provider_profile import ProviderProfile
from models.users import Users
from sqlalchemy.orm import scoped_session, sessionmaker

os.environ[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:postgres@localhost/fsa_rollback_per_test"


@pytest.fixture(scope="session")
def client():
    test_app = create_app()
    test_client = test_app.test_client()

    with test_app.app_context():
        yield test_client


@pytest.fixture(scope="session")
def database(test_client):
    db.create_all()

    yield db

    db.drop_all()


@pytest.fixture(autouse=True)
def enable_transactional_tests(database):
    """https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites"""
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


# @pytest.fixture
# def userA():
#     user = User(id=1, name="Alice")
#     db.session.add(user)
#     db.session.commit()

#     yield user


# @pytest.fixture
# def userB():
#     user = User(id=1, name="Bob")
#     db.session.add(user)
#     db.session.commit()

#     yield user


def create_user(first_name: str, last_name: str):
    display_name = first_name + " " + last_name
    user = Users(
        first_name=first_name,
        last_name=last_name,
        display_name=display_name,
        email=(f"{first_name}.{last_name}@test.com"),
    )

    return user


@pytest.fixture
def provider_user(database):
    user = create_user("Provider", "Provider")
    database.session.add(user)
    database.session.commit()

    provider = ProviderProfile(user_id=user.id, appointment_buffer_sec=1800)
    database.session.add(provider)

    database.session.commit()
    yield user


@pytest.fixture
def patient_user(database):
    user = create_user("Patient", "Patient")
    database.session.add(user)
    database.session.commit()

    patient = PatientProfile(user_id=user.id, cancer_status=CancerStatus.REMISSION)
    database.session.add(patient)

    database.session.commit()
    yield user


@pytest.fixture
def booked_appointment_in_one_week(database, provider_user, patient_user):
    start_time = datetime.utcnow() + timedelta(days=7)
    appointment = Appointment(
        patient_id=patient_user.patient_profile.id,
        provider_id=provider_user.provider_profile.id,
        start_time=start_time,
        end_time=start_time + timedelta(minutes=30),
        status=AppointmentStatus.BOOKED,
    )

    database.session.add(appointment)
    database.session.commit()
    yield appointment
