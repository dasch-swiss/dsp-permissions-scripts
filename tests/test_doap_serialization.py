import shutil
import unittest
from pathlib import Path

from dsp_permissions_scripts.models.doap import Doap, DoapTarget
from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.utils.doap_serialize import (
    deserialize_doaps_of_project,
    serialize_doaps_of_project,
)
from tests.test_scope_serialization import compare_scopes


class TestDoapSerialization(unittest.TestCase):
    shortcode = "1234"

    def tearDown(self) -> None:
        testdata_dir = Path(f"project_data/{self.shortcode}")
        if testdata_dir.is_dir():
            shutil.rmtree(testdata_dir)
    
    def test_doap_serialization(self):
        doap1 = Doap(
            target=DoapTarget(
                project="http://rdfh.ch/projects/MsOaiQkcQ7-QPxsYBKckfQ",
                group=BuiltinGroup.PROJECT_ADMIN,
            ),
            scope=PermissionScope.create(
                CR=[BuiltinGroup.PROJECT_ADMIN],
                V=[BuiltinGroup.PROJECT_MEMBER],
            ),
            doap_iri="http://rdfh.ch/doap-1",
        )
        doap2 = Doap(
            target=DoapTarget(
                project="http://rdfh.ch/projects/MsOaiQkcQ7-QPxsYBKckfQ",
                group=BuiltinGroup.PROJECT_MEMBER,
            ),
            scope=PermissionScope.create(
                D=[BuiltinGroup.SYSTEM_ADMIN],
                M=[BuiltinGroup.KNOWN_USER],
            ),
            doap_iri="http://rdfh.ch/doap-2",
        )
        serialize_doaps_of_project(
            project_doaps=[doap1, doap2],
            shortcode=self.shortcode,
            mode="original",
        )
        deserialized_doaps = deserialize_doaps_of_project(
            shortcode=self.shortcode, 
            mode="original",
        )
        self._compare_doaps(deserialized_doaps[0], doap1)
        self._compare_doaps(deserialized_doaps[1], doap2)

    def _compare_doaps(self, doap1: Doap, doap2: Doap) -> None:
        self.assertEqual(doap1.target, doap2.target)
        compare_scopes(doap1.scope, doap2.scope)
        self.assertEqual(doap1.doap_iri, doap2.doap_iri)


if __name__ == "__main__":
    unittest.main()