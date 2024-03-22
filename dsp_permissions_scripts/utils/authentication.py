import os

from dsp_permissions_scripts.models.host import Hosts


def get_login_credentials(host: str) -> tuple[str, str]:
    """
    Retrieve user email and password from the environment variables.
    In case of localhost, return the default email/password for localhost.
    """
    if host == Hosts.LOCALHOST:
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



def get_protocol(host: str) -> str:
    return "removethis"
