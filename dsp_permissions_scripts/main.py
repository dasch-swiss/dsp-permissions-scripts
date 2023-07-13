
from dotenv import load_dotenv

from dsp_permissions_scripts.authentication import get_env, get_token
from dsp_permissions_scripts.models.groups import Group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.permissions import (
    make_scope,
    update_all_doap_scopes_for_project,
    update_permissions_for_resources_and_values,
    get_doaps_for_project
)
from dsp_permissions_scripts.project import get_project_iri_by_shortcode


def main() -> None:
    # set login credentials from .env file as environment variables
    load_dotenv()
    host = Hosts.get_host("prod")
    shortcode = "0848"
    inspect_permissions(host, shortcode)
    # set_doaps(host, shortcode)
    # set_oaps(host)


def inspect_permissions(host: str, shortcode: str) -> None:
    """
    Prints the doaps for a project, provided a host and a shortcode.
    """
    user, pw = get_env(host)
    token = get_token(host, user, pw)
    project_iri = get_project_iri_by_shortcode(shortcode, host)
    doaps = get_doaps_for_project(project_iri, host, token)
    for d in doaps:
        print(d.json(indent=2))
        print()


def set_oaps(host: str) -> None:
    """
    sets the object access permissions for a list of objects (resources/properties) and each of their values.
    """
    user, pw = get_env(host)
    token = get_token(host, user, pw)
    # TODO: there should be defined common scopes, that should be useable by `Scopes.public`, `Scopes.private`, etc.
    new_scope = make_scope(
        change_rights=[Group.PROJECT_ADMIN, Group.CREATOR],
        view=[Group.UNKNOWN_USER, Group.KNOWN_USER],
        # delete=[Group.PROJECT_MEMBER]
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
    """
    sets all DOAPs for a project to a set scope.
    """
    # TODO: probably the scope should be provided as a parameter to this method
    user, pw = get_env(host)
    token = get_token(host, user, pw)
    project_iri = get_project_iri_by_shortcode(shortcode, host)
    # scope = an object encoding the information which group gets which permissions if this doap gets applied
    new_scope = make_scope(
        view=[Group.UNKNOWN_USER, Group.KNOWN_USER],
        change_rights=[Group.PROJECT_ADMIN],
        delete=[Group.CREATOR, Group.PROJECT_MEMBER]
    )
    update_all_doap_scopes_for_project(project_iri, new_scope, host, token)
    print("Finished successfully")


if __name__ == "__main__":
    main()
