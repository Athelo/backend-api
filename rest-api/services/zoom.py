import logging
from api.utils import get_api_url
import requests
import requests.auth
import urllib.parse as url_parse

CLIENT_ID = "uGg_8H7qSYmioNsz2I83aA"  # Fill this in with your client ID
CLIENT_SECRET = (
    "97TKYdJIh4QO8eBz1lj2okiDnSxcuw4q"  # Fill this in with your client secret
)
logger = logging.getLogger()


def get_redirect_url():
    return get_api_url() + "/zoom/callback"


def get_zoom_oath_url():
    encoded_redirect_url = url_parse.quote(get_redirect_url(), safe=" ")
    zoom_url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={encoded_redirect_url}"
    print(zoom_url)
    return zoom_url


def make_zoom_authorization_url():
    params = {
        "client_id": CLIENT_ID,
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
    client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
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
    return token_json["access_token"]
