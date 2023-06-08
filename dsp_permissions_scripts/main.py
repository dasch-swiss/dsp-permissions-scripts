# from getpass import getpass
# from time import sleep
import os

from dotenv import load_dotenv

from dsp_permissions_scripts.authentication import get_token
from dsp_permissions_scripts.permissions import (
    make_scope,
    update_all_doap_scopes_for_project,
    update_permissions_for_resources_and_values,
    get_doaps_for_project
)
from dsp_permissions_scripts.project import get_project_iri_by_shortcode

UNKNOWN_USER = "http://www.knora.org/ontology/knora-admin#UnknownUser"
KNOWN_USER = "http://www.knora.org/ontology/knora-admin#KnownUser"
CREATOR = "http://www.knora.org/ontology/knora-admin#Creator"
PROJECT_MEMBER = "http://www.knora.org/ontology/knora-admin#ProjectMember"
PROJECT_MEMBER = "http://www.knora.org/ontology/knora-admin#ProjectMember"
PROJECT_ADMIN = "http://www.knora.org/ontology/knora-admin#ProjectAdmin"
SYSTEM_ADMIN = "http://www.knora.org/ontology/knora-admin#SystemAdmin"


class Hosts:
    LOCALHOST = "localhost:3333"
    PROD = "api.dasch.swiss"
    TEST = "api.test.dasch.swiss"
    DEV = "api.dev.dasch.swiss"
    LS_PROD = "api.ls-prod.admin.ch"
    STAGING = "api.staging.dasch.swiss"

    @staticmethod
    def get_host(identifier: str) -> str:
        match identifier:
            case "localhost":
                return Hosts.LOCALHOST
            case "prod":
                return Hosts.PROD
            case _:
                return f"api.{identifier}.dasch.swiss"


def main() -> None:
    host = Hosts.get_host("0106-test-server")
    shortcode = "0806"
    inspect_permissions(host, shortcode)
    # set_doaps(host, shortcode)
    # set_object_permissions(host)


def inspect_permissions(host: str, shortcode: str) -> None:
    user, pw = get_env(host)
    token = get_token(host, user, pw)
    project_iri = get_project_iri_by_shortcode(shortcode, host)
    doaps = get_doaps_for_project(project_iri, host, token)
    for d in doaps:
        print(d.json(indent=2))
        print()


def set_object_permissions(host: str) -> None:
    user, pw = get_env(host)
    token = get_token(host, user, pw)
    new_scope = make_scope(
        change_rights=[PROJECT_ADMIN, CREATOR],
        view=[UNKNOWN_USER, KNOWN_USER],
        # delete=[PROJECT_MEMBER]
    )
    object_iris = [
        # "http://rdfh.ch/0810/_cyEQqI4T3-d_MIl0IAS2w",
        # "http://rdfh.ch/0810/9eUg68OWR66u26Bffrj0nQ",
        # "http://rdfh.ch/0810/bAZD7_qnSMCt9yVtTaCNqQ",
        # "http://rdfh.ch/0810/UigKXIqHSHSWomxUZ_gCvQ",
        # "http://rdfh.ch/0810/FaURJ8QaRY2TbUahi6QBog",
        # "http://rdfh.ch/0810/JYBrw1MARLKcrAHrJarrTQ",
        # "http://rdfh.ch/0810/UHJZN4OZQ7SKIpAHzeCkQw"
        "http://rdfh.ch/1234/QWh4ZIIiTuSxV0Ov3pc8ig"
    ]
    update_permissions_for_resources_and_values(object_iris, new_scope, host, token)


def set_doaps(host: str, shortcode: str) -> None:
    user, pw = get_env(host)
    token = get_token(host, user, pw)
    project_iri = get_project_iri_by_shortcode(shortcode, host)
    # scope = an object encoding the information which group gets which permissions if this doap gets applied
    new_scope = make_scope(
        view=[UNKNOWN_USER, KNOWN_USER],
        change_rights=[PROJECT_ADMIN],
        delete=[CREATOR, PROJECT_MEMBER]
    )
    update_all_doap_scopes_for_project(project_iri, new_scope, host, token)
    print("Finished successfully")


def get_env(host: str) -> tuple[str, str]:
    if host.startswith("localhost"):
        user = "root@example.com"
        pw = "test"
    else:
        user = os.getenv("DSP_USER_EMAIL") or ""
        pw = os.getenv("DSP_USER_PASSWORD") or ""
    assert user
    assert pw
    return user, pw


if __name__ == "__main__":
    load_dotenv()
    main()
