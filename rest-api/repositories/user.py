from models.users import Users
from models.database import db
from models.provider_profile import ProviderProfile
from repositories.utils import commit_entity
from flask import current_app as app
from api.constants import ALLOWED_ADMIN_DOMAINS
from auth.exceptions import UnauthorizedException
from models.admin_profile import AdminProfile


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
