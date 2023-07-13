import os
import requests


def get_token(host: str, email: str, pw: str) -> str:
    """
    requests an access token from the API, provided host, email and password.
    """
    url = f"https://{host}/v2/authentication"
    response = requests.post(url, json={"email": email, "password": pw}, timeout=5)
    assert response.status_code == 200
    token: str = response.json()["token"]
    return token


def get_login_credentials(host: str) -> tuple[str, str]:
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
    assert user
    assert pw
    return user, pw


def login(host: str) -> str:
    """
    Login with the DSP server

    Args:
        host: DSP server

    Returns:
        token: access token
    """
    user, pw = get_login_credentials(host)
    token = get_token(host, user, pw)
    return token
