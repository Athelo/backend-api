import os
from datetime import datetime, timedelta

import pytest
from models.admin_profile import AdminProfile
from models.appointments.appointment import Appointment, AppointmentStatus
from models.appointments.vonage_session import VonageSession
from models.patient_profile import CancerStatus, PatientProfile
from models.provider_profile import ProviderProfile
from models.users import Users

os.environ[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:postgres@localhost/fsa_rollback_per_test"


valid_token = {"uid": "foo", "email": "test@test.com"}

admin_user_email = "admin@athelohealth.com"

patient_user_email = "patient@gmail.com"
patient_user2_email = "patient2@gmail.com"

provider_user_email = "provider@gmail.com"


def create_user(first_name: str, last_name: str, email: str = None):
    display_name = first_name + " " + last_name
    if email is None:
        email = f"{first_name}.{last_name}@test.com"
    user = Users(
        first_name=first_name,
        last_name=last_name,
        display_name=display_name,
        email=email,
    )

    return user


@pytest.fixture()
def provider_user(database):
    user = create_user("Provider", "Provider", provider_user_email)
    database.session.add(user)
    database.session.commit()

    provider = ProviderProfile(user_id=user.id, appointment_buffer_sec=1800)
    database.session.add(provider)

    database.session.commit()
    yield user


@pytest.fixture()
def patient_user(database):
    user = create_user("Patient", "Patient", patient_user_email)
    database.session.add(user)
    database.session.commit()

    patient = PatientProfile(user_id=user.id, cancer_status=CancerStatus.REMISSION)
    database.session.add(patient)

    database.session.commit()
    yield user


@pytest.fixture()
def patient_user2(database):
    user = create_user("Patient", "Patient", patient_user2_email)
    database.session.add(user)
    database.session.commit()

    patient = PatientProfile(user_id=user.id, cancer_status=CancerStatus.ACTIVE)
    database.session.add(patient)

    database.session.commit()
    yield user


@pytest.fixture()
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


@pytest.fixture
def admin_user(database):
    user = create_user("Admin", "Admin", admin_user_email)
    database.session.add(user)
    database.session.commit()

    admin = AdminProfile(user_id=user.id)
    database.session.add(admin)

    database.session.commit()
    yield user


@pytest.fixture
def appointment_with_vonage_session(booked_appointment_in_one_week, database):
    vonage_session = VonageSession(
        appointment_id=booked_appointment_in_one_week.id, session_id="session_id"
    )
    database.session.add(vonage_session)
    database.session.commit()
    return booked_appointment_in_one_week
