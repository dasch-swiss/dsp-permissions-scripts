import os

from dsp_permissions_scripts.dsp_connection_service.dsp_connection_service import DspConnectionService


def _get_token(host: str, email: str, pw: str, dsp_connection: DspConnectionService) -> str:
    """requests an access token from the API, provided host, email and password."""
    return dsp_connection.get_token(host, email, pw)


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
    assert user
    assert pw
    return user, pw


def login(
    host: str,
    dsp_connection: DspConnectionService
) -> str:
    """
    Login with the DSP server

    Args:
        host: DSP server

    Returns:
        token: access token
    """
    user, pw = _get_login_credentials(host)
    token = _get_token(host, user, pw, dsp_connection)
    return token
