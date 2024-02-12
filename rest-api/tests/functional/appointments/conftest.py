from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from models.appointments.appointment import Appointment, AppointmentStatus
from models.appointments.vonage_session import VonageSession
from models.community_thread import CommunityThread
from models.users import Users


def create_appointment(
    provider_user: Users,
    patient_user: Users,
    database,
    start_time=datetime.utcnow() + timedelta(days=7),
    status=AppointmentStatus.BOOKED,
):
    end_time = start_time + timedelta(minutes=30)
    appointment = Appointment(
        provider_id=provider_user.provider_profile.id,
        patient_id=patient_user.patient_profile.id,
        start_time=start_time,
        end_time=end_time,
        status=status,
    )

    database.session.add(appointment)
    database.session.commit()

    vonage_info = VonageSession(appointment_id=appointment.id, session_id="session_id")

    database.session.add(vonage_info)
    database.session.commit()

    return appointment


@pytest.fixture
def booked_vonage_appointment(
    provider_user: Users,
    patient_user: Users,
    database,
):
    appointment = create_appointment(
        provider_user,
        patient_user,
        database,
    )

    return appointment


@pytest.fixture
def canceled_appointment_in_one_week(
    provider_user: Users, patient_user: Users, database
):
    appointment = create_appointment(
        provider_user,
        patient_user,
        database,
        datetime.utcnow() + timedelta(days=7),
        AppointmentStatus.CANCELLED,
    )
    return appointment


@pytest.fixture
def booked_appointment_in_two_weeks(
    provider_user: Users, patient_user: Users, database
):
    appointment = create_appointment(
        provider_user, patient_user, database, datetime.utcnow() + timedelta(days=14)
    )
    return appointment


@pytest.fixture
def booked_appointment_in_two_weeks_2_2(
    provider_user2: Users, patient_user2: Users, database
):
    appointment = create_appointment(
        provider_user2, patient_user2, database, datetime.utcnow() + timedelta(days=14)
    )
    return appointment


@pytest.fixture
def booked_appointment_in_four_weeks(
    provider_user: Users, patient_user: Users, database
):
    appointment = create_appointment(
        provider_user, patient_user, database, datetime.utcnow() + timedelta(weeks=4)
    )
    return appointment


@pytest.fixture
def booked_appointment_in_four_weeks_1_2(
    provider_user: Users, patient_user2: Users, database
):
    appointment = create_appointment(
        provider_user, patient_user2, database, datetime.utcnow() + timedelta(weeks=4)
    )
    return appointment
