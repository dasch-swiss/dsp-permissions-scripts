import time
from typing import Callable

import requests
from requests import ReadTimeout, RequestException
from urllib3.exceptions import ReadTimeoutError

from dsp_permissions_scripts.utils.get_logger import get_logger, get_timestamp

logger = get_logger(__name__)


def http_call_with_retry(action: Callable[..., requests.Response], err_msg: str) -> requests.Response:
    """
    Function that tries 7 times to execute an HTTP request.
    502 and 404 are catched, and the request is retried after a waiting time.
    The waiting times are 1, 2, 4, 8, 16, 32, 64 seconds.
    Use this only for actions that can be retried without side effects.

    Args:
        action: one of requests.get(), requests.post(), requests.put(), requests.delete()
        err_msg: this message is printed and logged when there is a problem with the call

    Raises:
        errors from the requests library

    Returns:
        response of the HTTP request
    """
    for i in range(7):
        try:
            response: requests.Response = action()
            if response.status_code == 200:
                return response
            retry_code = 500 <= response.status_code < 600 or response.status_code == 404
            try_again_later = "try again later" in response.text
            if retry_code or try_again_later:
                msg = f"{err_msg}. Retry request in {2 ** i} seconds... ({response.status_code}: {response.text})"
                print(f"{get_timestamp()}: SERVER ERROR: {msg}")
                logger.error(msg)
                continue
            return response
        except (TimeoutError, ReadTimeout, ReadTimeoutError, RequestException, ConnectionError):
            print(f"{get_timestamp()}: Server Error: Retry request in {2 ** i} seconds...")
            logger.error(f"Server Error: Retry request in {2 ** i} seconds...", exc_info=True)
            time.sleep(2**i)
            continue

    logger.error("Permanently unable to execute the API call. See logs for more details.")
    return action()
