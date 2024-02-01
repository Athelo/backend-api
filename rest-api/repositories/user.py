from models.users import Users
from models.database import db
from models.provider_profile import ProviderProfile
from api.utils import commit_entity_or_abort
from repositories.utils import try_commit_entity
from flask import current_app as app


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
    commit_entity_or_abort(provider_profile)


def update_provider_zoom_id_by_email(email: str, zoom_id: str) -> bool:
    user = get_user_by_email(email)
    print(email)
    print(zoom_id)
    if user is None:
        app.logger.error(f"No user for email {email}")
        return False

    if not user.is_provider:
        app.logger.error(
            f"Cannot update zoom info for user {user.id} because they are not a provider"
        )
        return False

    user.provider_profile.zoom_user_id = zoom_id

    return try_commit_entity(user.provider_profile)
