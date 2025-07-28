import os
import re

from dotenv import load_dotenv

from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.utils.dsp_client import DspClient
from dsp_permissions_scripts.utils.get_logger import get_logger

logger = get_logger(__name__)


def _get_login_credentials(host: str) -> tuple[str, str]:
    """
    Retrieve user email and password from the environment variables.
    In case of localhost, return the default email/password for localhost.
    """
    if host == Hosts.LOCALHOST:
        # When using a Prod-Dump locally, this is handy
        user = os.getenv("LOCALHOST_EMAIL") or "root@example.com"
        pw = os.getenv("LOCALHOST_PASSWORD") or "test"
    elif re.search(r"api.rdu-\d\d.dasch.swiss", host):
        user = os.getenv("RDU_TEST_EMAIL") or ""
        pw = os.getenv("RDU_TEST_PASSWORD") or ""
    elif host == Hosts.DEV:
        user = os.getenv("DEV_EMAIL") or ""
        pw = os.getenv("DEV_PASSWORD") or ""
    elif host == Hosts.STAGE:
        user = os.getenv("STAGE_EMAIL") or ""
        pw = os.getenv("STAGE_PASSWORD") or ""
    elif host == Hosts.RDU:
        user = os.getenv("RDU_EMAIL") or ""
        pw = os.getenv("RDU_PASSWORD") or ""
    elif host == Hosts.PROD:
        user = os.getenv("PROD_EMAIL") or ""
        pw = os.getenv("PROD_PASSWORD") or ""
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
    logger.info(f"Logging in to {host}...")
    load_dotenv()  # set login credentials from .env file as environment variables
    user, pw = _get_login_credentials(host)
    dsp_client = DspClient(host)
    dsp_client.login(user, pw)
    logger.info(f"Logged in to {host} successfully.")
    return dsp_client
