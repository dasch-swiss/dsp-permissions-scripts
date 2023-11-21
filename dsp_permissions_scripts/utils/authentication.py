import os

import requests

from dsp_permissions_scripts.models.api_error import ApiError


def _get_token(host: str, email: str, pw: str) -> str:
    """Requests an access token from DSP-API"""
    protocol = get_protocol(host)
    url = f"{protocol}://{host}/v2/authentication"
    response = requests.post(url, json={"email": email, "password": pw}, timeout=20)
    if response.status_code != 200:
        raise ApiError("Could not login", response.text, response.status_code)
    token: str = response.json()["token"]
    return token


def _get_login_credentials(host: str) -> tuple[str, str]:
    """
    Retrieve user email and password from the environment variables.
    In case of localhost, return the default email/password for localhost.
    """
    if host.startswith("localhost"):
        user = "root@example.com"
        pw = "test"
    else:
        user = os.getenv("DSP_USER_EMAIL") or ""
        pw = os.getenv("DSP_USER_PASSWORD") or ""
    if not user or not pw:
        raise NameError(
            "Missing credentials: Your username/password could not be retrieved. "
            "Please define 'DSP_USER_EMAIL' and 'DSP_USER_PASSWORD' in the file '.env'."
        )
    return user, pw


def login(host: str) -> str:
    """
    Login with the DSP server

    Args:
        host: DSP server

    Returns:
        token: access token
    """
    user, pw = _get_login_credentials(host)
    token = _get_token(host, user, pw)
    return token


def get_protocol(host: str) -> str:
    """Returns 'http' if host is localhost, otherwise 'https'"""
    return "http" if host.startswith("localhost") else "https"
