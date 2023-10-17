

import time
from typing import Any, Callable

import requests
from requests import ReadTimeout

from dsp_permissions_scripts.utils.get_logger import get_logger, get_timestamp

logger = get_logger(__name__)


def http_call_with_retry(
    action: Callable[..., Any],
) -> requests.Response:
    """
    Function that tries 7 times to execute an HTTP request.
    502 and 404 are catched, and the request is retried after a waiting time.
    The waiting times are 1, 2, 4, 8, 16, 32, 64 seconds.
    Use this only for actions that can be retried without side effects.

    Args:
        action: one of requests.get(), requests.post(), requests.put(), requests.delete()

    Raises:
        ValueError: if the action is not one of one of requests.get/post/put/delete
        Other Errors: errors from the requests library

    Returns:
        response of the HTTP request
    """
    if action not in (requests.get, requests.post, requests.put, requests.delete):
        raise ValueError(
            "This function can only be used with the methods get, post, put, and delete of the Python requests library."
        )
    for i in range(7):
        try:
            response: requests.Response = action()
            if response.status_code in [502, 404]:
                print(f"{get_timestamp()}: Server Error: Retry request in {2 ** i} seconds...")
                logger.error(f"Server Error: Retry request in {2 ** i} seconds... ({response.status_code}: {response.text})")
                continue
            return response
        except (TimeoutError, ReadTimeout, ReadTimeoutError):
            print(f"{get_timestamp()}: Server Error: Retry request in {2 ** i} seconds...")
            logger.error(f"Server Error: Retry request in {2 ** i} seconds...", exc_info=True)
            time.sleep(2**i)
            continue

    logger.error("Permanently unable to execute the API call. See logs for more details.")
    return action()
