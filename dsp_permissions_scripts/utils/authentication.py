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


def get_env(host: str) -> tuple[str, str]:
    """
    returns user email and password for a given host.
    """
    # TODO: this could definitely be improved, including function naming
    if host.startswith("localhost"):
        user = "root@example.com"
        pw = "test"
    else:
        user = os.getenv("DSP_USER_EMAIL") or ""
        pw = os.getenv("DSP_USER_PASSWORD") or ""
    assert user
    assert pw
    return user, pw
