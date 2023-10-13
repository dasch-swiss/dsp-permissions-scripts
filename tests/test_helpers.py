import unittest

from dsp_permissions_scripts.models import builtin_groups
from dsp_permissions_scripts.utils.helpers import sort_groups


class TestHelpers(unittest.TestCase):
    def test_sort_groups(self) -> None:
        groups_original = [
            "http://www.knora.org/ontology/knora-admin#C_CustomGroup",
            builtin_groups.UNKNOWN_USER,
            builtin_groups.PROJECT_ADMIN,
            builtin_groups.PROJECT_MEMBER,
            builtin_groups.CREATOR,
            "http://www.knora.org/ontology/knora-admin#A_CustomGroup",
            "http://www.knora.org/ontology/knora-admin#B_CustomGroup",
            builtin_groups.KNOWN_USER,
            builtin_groups.SYSTEM_ADMIN,
        ]
        groups_expected = [
            builtin_groups.SYSTEM_ADMIN,
            builtin_groups.CREATOR,
            builtin_groups.PROJECT_ADMIN,
            builtin_groups.PROJECT_MEMBER,
            builtin_groups.KNOWN_USER,
            builtin_groups.UNKNOWN_USER,
            "http://www.knora.org/ontology/knora-admin#A_CustomGroup",
            "http://www.knora.org/ontology/knora-admin#B_CustomGroup",
            "http://www.knora.org/ontology/knora-admin#C_CustomGroup",
        ]
        groups_returned = sort_groups(groups_original=groups_original)
        self.assertEqual(groups_returned, groups_expected)


if __name__ == "__main__":
    unittest.main()
