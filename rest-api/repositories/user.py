from api.constants import ALLOWED_ADMIN_DOMAINS
from auth.exceptions import UnauthorizedException
from flask import current_app as app
from models.admin_profile import AdminProfile
from models.caregiver_profile import CaregiverProfile
from models.database import db
from models.patient_profile import CancerStatus, PatientProfile
from models.provider_profile import ProviderProfile
from models.users import Users

from repositories.utils import commit_entity


def get_user_by_email(email: str) -> Users:
    return db.session.query(Users).filter(Users.email == email).one_or_none()


def get_user_by_provider_id(id: int) -> Users:
    provider = db.session.get(ProviderProfile, id)
    if provider is None:
        return None
    return provider.user


def set_provider_zoom_refresh_token(
    provider_profile: ProviderProfile, refresh_token: str
) -> None:
    provider_profile.zoom_refresh_token = refresh_token
    commit_entity(provider_profile)


def update_provider_zoom_id_by_email(email: str, zoom_id: str) -> bool:
    user = get_user_by_email(email)
    if user is None:
        app.logger.error(f"No user for email {email}")
        return False

    if not user.is_provider:
        app.logger.error(
            f"Cannot update zoom info for user {user.id} because they are not a provider"
        )
        return False

    user.provider_profile.zoom_user_id = zoom_id

    commit_entity(user.provider_profile)
    return True


def create_admin_profile_for_user(user: Users):
    domain = user.email.split("@")[1]

    if not any(
        allowed_domain
        for allowed_domain in ALLOWED_ADMIN_DOMAINS
        if allowed_domain == domain
    ):
        raise UnauthorizedException("User's email is not on a valid admin domain")

    admin_profile = AdminProfile(user_id=user.id)
    commit_entity(admin_profile)


def create_provider_profile_for_user(user: Users, appointment_buffer_sec: int = 1800):
    profile = ProviderProfile(
        user_id=user.id, appointment_buffer_sec=appointment_buffer_sec
    )
    commit_entity(profile)


def create_patient_profile_for_user(user: Users, cancer_status: CancerStatus):
    profile = PatientProfile(user_id=user.id, cancer_status=cancer_status)
    commit_entity(profile)


def create_caregiver_profile_for_user(user: Users):
    profile = CaregiverProfile(user_id=user.id)
    commit_entity(profile)


def deactivate_user(user: Users):
    if user.is_provider:
        user.provider_profile.active = False
        db.session.add(user.provider_profile)
    if user.is_admin:
        user.admin_profile.active = False
        db.session.add(user.admin_profile)
    if user.is_patient:
        user.patient_profile.active = False
        db.session.add(user.patient_profile)
    if user.is_caregiver:
        user.caregiver_profile = False
        db.session.add(user.caregiver_profile)

    user.active = False
    commit_entity(user)
