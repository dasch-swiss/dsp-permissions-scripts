import os
import re

from dotenv import load_dotenv

from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.utils.dsp_client import DspClient


def _get_login_credentials(host: str) -> tuple[str, str]:
    """
    Retrieve user email and password from the environment variables.
    In case of localhost, return the default email/password for localhost.
    """
    if host == Hosts.LOCALHOST:
        user = "root@example.com"
        pw = "test"
    elif host == Hosts.RDU_STAGE:
        user = os.getenv("RDU_STAGE_EMAIL") or ""
        pw = os.getenv("RDU_STAGE_PASSWORD") or ""
    elif re.search(r"api.rdu-\d\d.dasch.swiss", host):
        user = os.getenv("RDU_TEST_EMAIL") or ""
        pw = os.getenv("RDU_TEST_PASSWORD") or ""
    elif host == Hosts.DEV:
        user = os.getenv("DEV_EMAIL") or ""
        pw = os.getenv("DEV_PASSWORD") or ""
    else:
        user = os.getenv("PROD_EMAIL") or ""
        pw = os.getenv("PROD_PASSWORD") or ""
    if not user or not pw:
        raise NameError(
            "Missing credentials: Your username/password could not be retrieved. "
            "Please define '<ENV>_EMAIL' and '<ENV>_PASSWORD' in the file '.env'."
        )
    return user, pw


def login(host: str) -> DspClient:
    """
    Create a DspClient instance that will handle the network traffic to the DSP server.

    Args:
        host: DSP server

    Returns:
        dsp_client: client that knows how to access the DSP server (i.e. that has a token)
    """
    load_dotenv()  # set login credentials from .env file as environment variables
    user, pw = _get_login_credentials(host)
    dsp_client = DspClient(host)
    dsp_client.login(user, pw)
    return dsp_client
