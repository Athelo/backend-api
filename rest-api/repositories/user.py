from models.users import Users
from models.database import db
from models.provider_profile import ProviderProfile


def get_user_by_email(email: str) -> Users:
    return db.session.query(Users).filter(Users.email == email).one_or_none()


def get_user_by_provider_id(id: int) -> Users:
    provider = db.session.get(ProviderProfile, id)
    if provider is None:
        return None
    return provider.user


def set_provider_zoom_refresh_token(
    provider_profile: ProviderProfile, refresh_token: str
):
    provider_profile.zoom_refresh_token = refresh_token
    db.session.add(provider_profile)
    db.session.commit()
