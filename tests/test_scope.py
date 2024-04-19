import re

import pytest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.errors import EmptyScopeError
from dsp_permissions_scripts.models.scope import PermissionScope


class TestScopeCreation:
    def test_valid_scope(self) -> None:
        scope = PermissionScope(
            CR=frozenset({group.SYSTEM_ADMIN}),
            D=frozenset({group.PROJECT_ADMIN}),
            M=frozenset({group.PROJECT_MEMBER, group.KNOWN_USER}),
            V=frozenset({group.UNKNOWN_USER}),
        )
        assert scope.CR == frozenset({group.SYSTEM_ADMIN})
        assert scope.D == frozenset({group.PROJECT_ADMIN})
        assert scope.M == frozenset({group.PROJECT_MEMBER, group.KNOWN_USER})
        assert scope.V == frozenset({group.UNKNOWN_USER})
        assert scope.RV == frozenset()

    def test_valid_scope_create(self) -> None:
        scope = PermissionScope.create(
            CR={group.SYSTEM_ADMIN},
            D={group.PROJECT_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
            V={group.UNKNOWN_USER},
        )
        assert scope.CR == frozenset({group.SYSTEM_ADMIN})
        assert scope.D == frozenset({group.PROJECT_ADMIN})
        assert scope.M == frozenset({group.PROJECT_MEMBER, group.KNOWN_USER})
        assert scope.V == frozenset({group.UNKNOWN_USER})
        assert scope.RV == frozenset()

    def test_valid_scope_from_dict(self) -> None:
        scope = PermissionScope.from_dict(
            {
                "CR": [group.SYSTEM_ADMIN.val],
                "D": [group.PROJECT_ADMIN.val],
                "M": [group.PROJECT_MEMBER.val, group.KNOWN_USER.val],
                "V": [group.UNKNOWN_USER.val],
            }
        )
        assert scope.CR == frozenset({group.SYSTEM_ADMIN})
        assert scope.D == frozenset({group.PROJECT_ADMIN})
        assert scope.M == frozenset({group.PROJECT_MEMBER, group.KNOWN_USER})
        assert scope.V == frozenset({group.UNKNOWN_USER})
        assert scope.RV == frozenset()

    def test_create_empty_scope(self) -> None:
        with pytest.raises(EmptyScopeError):
            PermissionScope.create()
        with pytest.raises(EmptyScopeError):
            PermissionScope()
        with pytest.raises(EmptyScopeError):
            PermissionScope.from_dict({})

    def test_same_group_in_multiple_fields(self) -> None:
        with pytest.raises(ValueError, match=re.escape("must not occur in more than one field")):
            PermissionScope.create(
                CR={group.PROJECT_ADMIN},
                D={group.PROJECT_ADMIN},
                V={group.UNKNOWN_USER, group.KNOWN_USER},
            )


class TestAdd:
    def test_add_to_scope(self) -> None:
        scope = PermissionScope.create(
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        )
        scope = scope.add("CR", group.PROJECT_ADMIN)
        scope_expected = PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        )
        assert scope == scope_expected

    def test_add_same_group_to_same_permission(self) -> None:
        scope = PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            V={group.UNKNOWN_USER, group.KNOWN_USER},
        )
        rgx = "Group 'val='http://www.knora.org/ontology/knora-admin#ProjectAdmin'' is already in permission 'CR'"
        with pytest.raises(ValueError, match=re.escape(rgx)):
            _ = scope.add("CR", group.PROJECT_ADMIN)

    def test_add_same_group_to_different_permission(self) -> None:
        scope = PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            V={group.UNKNOWN_USER, group.KNOWN_USER},
        )
        with pytest.raises(ValueError, match=re.escape("must not occur in more than one field")):
            _ = scope.add("RV", group.PROJECT_ADMIN)


class TestRemove:
    def test_remove_from_scope(self) -> None:
        scope = PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        )
        scope = scope.remove("CR", group.PROJECT_ADMIN)
        scope_expected = PermissionScope.create(
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        )
        assert scope == scope_expected

    def test_remove_inexisting_group(self) -> None:
        scope = PermissionScope.create(
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
        )
        with pytest.raises(ValueError, match=re.escape("is not in permission 'D'")):
            _ = scope.remove("D", group.UNKNOWN_USER)

    def test_remove_from_empty_perm(self) -> None:
        scope = PermissionScope.create(
            D={group.PROJECT_ADMIN},
            V={group.PROJECT_MEMBER, group.UNKNOWN_USER},
        )
        with pytest.raises(ValueError, match=re.escape("is not in permission 'CR'")):
            _ = scope.remove("CR", group.PROJECT_ADMIN)


class TestGet:
    def test_get(self) -> None:
        scope = PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
            V={group.UNKNOWN_USER},
        )
        assert scope.get("CR") == frozenset({group.PROJECT_ADMIN})
        assert scope.get("D") == frozenset({group.SYSTEM_ADMIN})
        assert scope.get("M") == frozenset({group.PROJECT_MEMBER, group.KNOWN_USER})
        assert scope.get("V") == frozenset({group.UNKNOWN_USER})
        assert scope.get("RV") == frozenset()

    def test_get_inexisting_perm(self) -> None:
        scope = PermissionScope.create(
            CR={group.PROJECT_ADMIN},
            D={group.SYSTEM_ADMIN},
            M={group.PROJECT_MEMBER, group.KNOWN_USER},
            V={group.UNKNOWN_USER},
        )
        with pytest.raises(ValueError, match=re.escape("Permission 'foo' not in")):
            _ = scope.get("foo")


class TestRemoveDuplicatesFromKwargs:
    def test_remove_duplicates_from_kwargs_CR(self) -> None:
        original: dict[str, list[str]] = {
            "CR": ["knora-admin:ProjectAdmin"],
            "D": ["knora-admin:ProjectAdmin"],
            "M": ["knora-admin:ProjectAdmin"],
            "V": ["knora-admin:ProjectAdmin"],
            "RV": ["knora-admin:ProjectAdmin"],
        }
        expected = {"CR": ["knora-admin:ProjectAdmin"], "D": [], "M": [], "V": [], "RV": []}
        assert expected == PermissionScope._remove_duplicates_from_kwargs(original)

    def test_remove_duplicates_from_kwargs_D(self) -> None:
        original: dict[str, list[str]] = {
            "CR": [],
            "D": ["knora-admin:ProjectAdmin"],
            "M": ["knora-admin:ProjectAdmin"],
            "V": ["knora-admin:ProjectAdmin"],
            "RV": ["knora-admin:ProjectAdmin"],
        }
        expected = {"CR": [], "D": ["knora-admin:ProjectAdmin"], "M": [], "V": [], "RV": []}
        assert expected == PermissionScope._remove_duplicates_from_kwargs(original)

    def test_remove_duplicates_from_kwargs_RV(self) -> None:
        original: dict[str, list[str]] = {"CR": [], "D": [], "M": [], "V": [], "RV": ["knora-admin:ProjectAdmin"]}
        expected: dict[str, list[str]] = {"CR": [], "D": [], "M": [], "V": [], "RV": ["knora-admin:ProjectAdmin"]}
        assert expected == PermissionScope._remove_duplicates_from_kwargs(original)

    def test_remove_duplicates_from_kwargs_mixed(self) -> None:
        original: dict[str, list[str]] = {
            "CR": ["knora-admin:ProjectAdmin"],
            "D": ["knora-admin:ProjectMember"],
            "M": ["knora-admin:ProjectMember"],
            "V": ["knora-admin:ProjectMember"],
            "RV": ["knora-admin:ProjectMember"],
        }
        expected = {"CR": ["knora-admin:ProjectAdmin"], "D": ["knora-admin:ProjectMember"], "M": [], "V": [], "RV": []}
        assert expected == PermissionScope._remove_duplicates_from_kwargs(original)

    def test_remove_duplicates_from_kwargs_mixed_M(self) -> None:
        original: dict[str, list[str]] = {
            "CR": ["knora-admin:ProjectAdmin"],
            "D": [],
            "M": ["knora-admin:ProjectMember"],
            "V": ["knora-admin:ProjectMember"],
            "RV": ["knora-admin:ProjectMember"],
        }
        expected = {"CR": ["knora-admin:ProjectAdmin"], "D": [], "M": ["knora-admin:ProjectMember"], "V": [], "RV": []}
        assert expected == PermissionScope._remove_duplicates_from_kwargs(original)

    def test_remove_duplicates_from_kwargs_mixed_and_multiple(self) -> None:
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
