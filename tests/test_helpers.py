import unittest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.utils.helpers import sort_groups

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)

class TestHelpers(unittest.TestCase):
    def test_sort_groups(self) -> None:
        groups_original = [
            group.Group(val="http://www.knora.org/ontology/knora-admin#C_CustomGroup"),
            group.UNKNOWN_USER,
            group.PROJECT_ADMIN,
            group.PROJECT_MEMBER,
            group.CREATOR,
            group.Group(val="http://www.knora.org/ontology/knora-admin#A_CustomGroup"),
            group.Group(val="http://www.knora.org/ontology/knora-admin#B_CustomGroup"),
            group.KNOWN_USER,
            group.SYSTEM_ADMIN,
        ]
        groups_expected = [
            group.SYSTEM_ADMIN,
            group.CREATOR,
            group.PROJECT_ADMIN,
            group.PROJECT_MEMBER,
            group.KNOWN_USER,
            group.UNKNOWN_USER,
            group.Group(val="http://www.knora.org/ontology/knora-admin#A_CustomGroup"),
            group.Group(val="http://www.knora.org/ontology/knora-admin#B_CustomGroup"),
            group.Group(val="http://www.knora.org/ontology/knora-admin#C_CustomGroup"),
        ]
        groups_returned = sort_groups(groups_original)
        self.assertEqual(groups_returned, groups_expected)


if __name__ == "__main__":
    unittest.main()
