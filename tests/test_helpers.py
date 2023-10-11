import unittest

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.utils.helpers import sort_groups


class TestHelpers(unittest.TestCase):

    def test_sort_groups(self) -> None:
        groups_original = [
            "http://www.knora.org/ontology/knora-admin#C_CustomGroup",
            BuiltinGroup.UNKNOWN_USER.value,
            BuiltinGroup.PROJECT_ADMIN.value,
            BuiltinGroup.PROJECT_MEMBER.value,
            BuiltinGroup.CREATOR.value,
            "http://www.knora.org/ontology/knora-admin#A_CustomGroup",
            "http://www.knora.org/ontology/knora-admin#B_CustomGroup",
            BuiltinGroup.KNOWN_USER.value,
            BuiltinGroup.SYSTEM_ADMIN.value,
        ]
        groups_expected = [
            BuiltinGroup.SYSTEM_ADMIN.value,
            BuiltinGroup.CREATOR.value,
            BuiltinGroup.PROJECT_ADMIN.value,
            BuiltinGroup.PROJECT_MEMBER.value,
            BuiltinGroup.KNOWN_USER.value,
            BuiltinGroup.UNKNOWN_USER.value,
            "http://www.knora.org/ontology/knora-admin#A_CustomGroup",
            "http://www.knora.org/ontology/knora-admin#B_CustomGroup",
            "http://www.knora.org/ontology/knora-admin#C_CustomGroup",
        ]
        groups_returned = sort_groups(groups_original=groups_original)
        self.assertEqual(groups_returned, groups_expected)


if __name__ == "__main__":
    unittest.main()
