import re

import pytest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from tests.test_scope_serialization import compare_scopes


def test_scope_validation_on_creation() -> None:
    with pytest.raises(ValueError, match=re.escape("must not occur in more than one field")):
        PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            D={group.PROJECT_ADMIN},
            V={group.UNKNOWN_USER, group.KNOWN_USER},
        )


def test_scope_validation_on_add_to_same_permission() -> None:
    scope = PermissionScope.create(
        CR={group.PROJECT_ADMIN},
        V={group.UNKNOWN_USER, group.KNOWN_USER},
    )
    rgx = "Group 'val='http://www.knora.org/ontology/knora-admin#ProjectAdmin'' is already in permission 'CR'"
    with pytest.raises(ValueError, match=re.escape(rgx)):
        _ = scope.add("CR", group.PROJECT_ADMIN)


def test_scope_validation_on_add_to_different_permission() -> None:
    scope = PermissionScope.create(
        CR={group.PROJECT_ADMIN},
        V={group.UNKNOWN_USER, group.KNOWN_USER},
    )
    with pytest.raises(ValueError, match=re.escape("must not occur in more than one field")):
        _ = scope.add("RV", group.PROJECT_ADMIN)


def test_add_to_scope() -> None:
    scope = PermissionScope.create(
        D={group.SYSTEM_ADMIN},
        M={group.PROJECT_MEMBER, group.KNOWN_USER},
    )
    scope_added = scope.add("CR", group.PROJECT_ADMIN)
    compare_scopes(
        scope1=scope_added,
        scope2=PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        ),
    )


def test_remove_inexisting_group() -> None:
    scope = PermissionScope.create(
        D={group.SYSTEM_ADMIN},
        M={group.PROJECT_MEMBER, group.KNOWN_USER},
    )
    with pytest.raises(ValueError, match=re.escape("is not in permission 'D'")):
        _ = scope.remove("D", group.UNKNOWN_USER)


def test_remove_from_empty_perm() -> None:
    scope = PermissionScope.create(
        D={group.PROJECT_ADMIN},
        V={group.PROJECT_MEMBER, group.UNKNOWN_USER},
    )
    with pytest.raises(ValueError, match=re.escape("is not in permission 'CR'")):
        _ = scope.remove("CR", group.PROJECT_ADMIN)


def test_remove_from_scope() -> None:
    scope = PermissionScope.create(
        CR={group.PROJECT_ADMIN},
        D={group.SYSTEM_ADMIN},
        M={group.PROJECT_MEMBER, group.KNOWN_USER},
    )
    scope_removed = scope.remove("CR", group.PROJECT_ADMIN)
    compare_scopes(
        scope1=scope_removed,
        scope2=PermissionScope.create(
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        ),
    )


def test_remove_duplicates_from_kwargs_CR() -> None:
    original: dict[str, list[str]] = {
        "CR": ["knora-admin:ProjectAdmin"],
        "D": ["knora-admin:ProjectAdmin"],
        "M": ["knora-admin:ProjectAdmin"],
        "V": ["knora-admin:ProjectAdmin"],
        "RV": ["knora-admin:ProjectAdmin"],
    }
    expected = {"CR": ["knora-admin:ProjectAdmin"], "D": [], "M": [], "V": [], "RV": []}
    assert expected == PermissionScope._remove_duplicates_from_kwargs(original)


def test_remove_duplicates_from_kwargs_D() -> None:
    original: dict[str, list[str]] = {
        "CR": [],
        "D": ["knora-admin:ProjectAdmin"],
        "M": ["knora-admin:ProjectAdmin"],
        "V": ["knora-admin:ProjectAdmin"],
        "RV": ["knora-admin:ProjectAdmin"],
    }
    expected = {"CR": [], "D": ["knora-admin:ProjectAdmin"], "M": [], "V": [], "RV": []}
    assert expected == PermissionScope._remove_duplicates_from_kwargs(original)


def test_remove_duplicates_from_kwargs_RV() -> None:
    original: dict[str, list[str]] = {"CR": [], "D": [], "M": [], "V": [], "RV": ["knora-admin:ProjectAdmin"]}
    expected: dict[str, list[str]] = {"CR": [], "D": [], "M": [], "V": [], "RV": ["knora-admin:ProjectAdmin"]}
    assert expected == PermissionScope._remove_duplicates_from_kwargs(original)


def test_remove_duplicates_from_kwargs_mixed() -> None:
    original: dict[str, list[str]] = {
        "CR": ["knora-admin:ProjectAdmin"],
        "D": ["knora-admin:ProjectMember"],
        "M": ["knora-admin:ProjectMember"],
        "V": ["knora-admin:ProjectMember"],
        "RV": ["knora-admin:ProjectMember"],
    }
    expected = {"CR": ["knora-admin:ProjectAdmin"], "D": ["knora-admin:ProjectMember"], "M": [], "V": [], "RV": []}
    assert expected == PermissionScope._remove_duplicates_from_kwargs(original)


def test_remove_duplicates_from_kwargs_mixed_M() -> None:
    original: dict[str, list[str]] = {
        "CR": ["knora-admin:ProjectAdmin"],
        "D": [],
        "M": ["knora-admin:ProjectMember"],
        "V": ["knora-admin:ProjectMember"],
        "RV": ["knora-admin:ProjectMember"],
    }
    expected = {"CR": ["knora-admin:ProjectAdmin"], "D": [], "M": ["knora-admin:ProjectMember"], "V": [], "RV": []}
    assert expected == PermissionScope._remove_duplicates_from_kwargs(original)


def test_remove_duplicates_from_kwargs_mixed_and_multiple() -> None:
    original: dict[str, list[str]] = {
        "CR": ["knora-admin:ProjectAdmin"],
        "D": [],
        "M": ["knora-admin:ProjectMember", "knora-admin:ProjectAdmin", "knora-admin:KnownUser"],
        "V": ["knora-admin:ProjectMember", "knora-admin:ProjectAdmin"],
        "RV": ["knora-admin:ProjectMember", "knora-admin:KnownUser"],
    }
    expected = {
        "CR": ["knora-admin:ProjectAdmin"],
        "D": [],
        "M": ["knora-admin:ProjectMember", "knora-admin:KnownUser"],
        "V": [],
        "RV": [],
    }
    assert expected == PermissionScope._remove_duplicates_from_kwargs(original)


if __name__ == "__main__":
    pytest.main([__file__])
