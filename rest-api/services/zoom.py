import logging
from api.utils import get_api_url
import requests
import requests.auth
import urllib.parse as url_parse
from models.users import Users
from datetime import datetime
from repositories.user import set_provider_zoom_refresh_token, get_user_by_email
from flask import current_app as app
from models.provider_profile import ProviderProfile


ZOOM_ACCOUNT_EMAIL = "stephanie@athelohealth.com"


def get_redirect_url():
    return get_api_url() + "/zoom/callback"


def get_zoom_oath_url():
    encoded_redirect_url = url_parse.quote(get_redirect_url(), safe=" ")
    zoom_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={app.config.get('ZOOM_CLIENT_ID')}&redirect_uri={encoded_redirect_url}"
    return zoom_url


def make_zoom_authorization_url():
    params = {
        "client_id": app.config.get("ZOOM_CLIENT_ID"),
        "response_type": "code",
        "redirect_uri": get_redirect_url(),
    }
    url = "https://zoom.us/oauth/authorize?" + url_parse.urlencode(params)
    return url


def get_zoom_user_profile(access_token):
    headers = {"Authorization": "bearer " + access_token}
    response = requests.get("https://api.zoom.us/v2/users/me", headers=headers)
    return response.json()


def get_zoom_user_email(access_token):
    profile_json = get_zoom_user_profile(access_token)
    return profile_json["email"]


def get_zoom_token(code):
    client_auth = requests.auth.HTTPBasicAuth(
        app.config.get("ZOOM_CLIENT_ID"), app.config.get("ZOOM_CLIENT_SECRET")
    )
    post_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": get_redirect_url(),
    }

    response = requests.post(
        "https://zoom.us/oauth/token", auth=client_auth, data=post_data
    )
    token_json = response.json()
    return token_json["access_token"], token_json["refresh_token"]


def refresh_zoom_token(refresh_token: str):
    client_auth = requests.auth.HTTPBasicAuth(
        app.config.get("ZOOM_CLIENT_ID"), app.config.get("ZOOM_CLIENT_SECRET")
    )
    post_data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    response = requests.post(
        "https://zoom.us/oauth/token", auth=client_auth, data=post_data
    )
    token_json = response.json()
    return token_json["access_token"], token_json["refresh_token"]


def get_provider_zoom_access_token(provider_profile: ProviderProfile) -> str:
    access_token, refresh_token = refresh_zoom_token(
        provider_profile.zoom_refresh_token
    )
    set_provider_zoom_refresh_token(provider_profile, refresh_token)
    return access_token


def create_zoom_meeting_with_provider(
    provider_user: Users,
    start_time: datetime,
    topic: str,
    duration: int = 30,
):
    if not provider_user.is_provider:
        raise ValueError("User must be a provider")

    if provider_user.provider_profile.zoom_user_id is None:
        raise ValueError("Provider is missing a  zoom user id")

    if provider_user.provider_profile.zoom_refresh_token is None:
        app.logger.info(
            "Provider does not have zoom authentication information - using Athelo account auth"
        )
        access_token = get_provider_zoom_access_token(
            get_user_by_email(ZOOM_ACCOUNT_EMAIL).provider_profile
        )
    else:
        access_token = get_provider_zoom_access_token(provider_user.provider_profile)

    print(
        f"User {provider_user.id} ({provider_user.email}) with zoom id {provider_user.provider_profile.zoom_user_id}"
    )

    create_meeting_url = f"https://api.zoom.us/v2/users/{provider_user.provider_profile.zoom_user_id}/meetings"

    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "topic": topic,
        "duration": duration,
        "start_time": start_time.isoformat(),
    }

    response = requests.post(create_meeting_url, headers=headers, json=payload)

    if response.status_code == 201:
        meeting_id = response.json()["id"]
        app.logger.info(f"Meeting created successfully, meeting ID: {meeting_id}")
    else:
        # The request failed, raise an exception
        raise requests.exceptions.HTTPError(
            "Failed to create meeting", response=response
        )

    return response.json()


def get_zoom_users_for_account() -> dict:
    user = get_user_by_email(ZOOM_ACCOUNT_EMAIL)
    if not user.is_provider:
        raise ValueError("User must be a provider")

    if (
        user.provider_profile.zoom_user_id is None
        or user.provider_profile.zoom_refresh_token is None
    ):
        raise ValueError(
            "Provider does not have zoom authentication information - using Athelo account"
        )

    if user.provider_profile.zoom_user_id is None:
        raise ValueError(
            "Provider doesn't have a zoom_id configured - are they a part of the athelo account?"
        )

    access_token, refresh_token = refresh_zoom_token(
        user.provider_profile.zoom_refresh_token
    )

    set_provider_zoom_refresh_token(user.provider_profile, refresh_token)

    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.zoom.us/v2/users?status=active"
    response = requests.get(
        url,
        headers=headers,
    )
    zoom_users = response.json()["users"]
    print(zoom_users)
    return zoom_users
