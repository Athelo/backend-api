import logging
from api.utils import get_api_url
import requests
import requests.auth
import urllib.parse as url_parse
from models.users import Users
from datetime import datetime
from repositories.user import set_provider_zoom_refresh_token
from flask import current_app as app


logger = logging.getLogger()


def get_zoom_client_id():
    return app.config.get("ZOOM_CLIENT_ID")


def get_zoom_client_secret():
    return app.config.get("ZOOM_CLIENT_SECRET")


def get_redirect_url():
    return get_api_url() + "/zoom/callback"


def get_zoom_oath_url():
    encoded_redirect_url = url_parse.quote(get_redirect_url(), safe=" ")
    zoom_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={get_zoom_client_id()}&redirect_uri={encoded_redirect_url}"
    return zoom_url


def make_zoom_authorization_url():
    params = {
        "client_id": get_zoom_client_id(),
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
        get_zoom_client_id(), get_zoom_client_secret()
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
    print(token_json)
    return token_json["access_token"], token_json["refresh_token"]


def refresh_zoom_token(refresh_token: str):
    client_auth = requests.auth.HTTPBasicAuth(
        get_zoom_client_id(), get_zoom_client_secret()
    )
    post_data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    response = requests.post(
        "https://zoom.us/oauth/token", auth=client_auth, data=post_data
    )
    token_json = response.json()
    print(token_json)
    return token_json["access_token"], token_json["refresh_token"]


def create_zoom_meeting_with_provider(
    user: Users,
    start_time: datetime,
    topic: str,
    duration: int = 30,
):
    if not user.is_provider:
        raise ValueError("User must be a provider")

    print(user.provider_profile.__dict__)

    if (
        user.provider_profile.zoom_user_id is None
        or user.provider_profile.zoom_refresh_token is None
    ):
        raise ValueError("Provider does not have zoom authorized")

    create_meeting_url = (
        f"https://api.zoom.us/v2/users/{user.provider_profile.zoom_user_id}/meetings"
    )

    access_token, refresh_token = refresh_zoom_token(
        user.provider_profile.zoom_refresh_token
    )

    set_provider_zoom_refresh_token(user.provider_profile, refresh_token)

    # The request headers
    headers = {"Authorization": f"Bearer {access_token}"}

    # The request body
    payload = {
        "topic": topic,
        "duration": duration,
        "start_time": start_time.isoformat(),
    }

    # Make the request to create the meeting
    response = requests.post(create_meeting_url, headers=headers, json=payload)

    # Check the response status code
    if response.status_code == 201:
        # The request was successful, get the meeting ID
        meeting_id = response.json()["id"]
        print(f"Meeting created successfully, meeting ID: {meeting_id}")
    else:
        # The request failed, raise an exception
        print(response)
        raise requests.exceptions.HTTPError(
            "Failed to create meeting", response=response
        )

    return response.json()
