import shutil
import unittest
from pathlib import Path

from dsp_permissions_scripts.ap.ap_model import Ap, ApValue
from dsp_permissions_scripts.ap.ap_serialize import (
    deserialize_aps_of_project,
    serialize_aps_of_project,
)
from dsp_permissions_scripts.models import builtin_groups


class TestApSerialization(unittest.TestCase):
    shortcode = "1234"
    project_iri = "http://rdfh.ch/projects/MsOaiQkcQ7-QPxsYBKckfQ"

    def tearDown(self) -> None:
        testdata_dir = Path(f"project_data/{self.shortcode}")
        if testdata_dir.is_dir():
            shutil.rmtree(testdata_dir)
    
    def test_ap_serialization(self):
        ap1 = Ap(
            forGroup=builtin_groups.PROJECT_ADMIN,
            forProject=self.project_iri,
            hasPermissions=frozenset({ApValue.ProjectAdminGroupRestrictedPermission}),
            iri="http://rdfh.ch/ap-1",
        )
        ap2 = Ap(
            forGroup=builtin_groups.KNOWN_USER,
            forProject=self.project_iri,
            hasPermissions=frozenset({ApValue.ProjectResourceCreateRestrictedPermission}),
            iri="http://rdfh.ch/ap-2",
        )
        serialize_aps_of_project(
            project_aps=[ap1, ap2],
            shortcode=self.shortcode,
            mode="original",
        )
        deserialized_aps = deserialize_aps_of_project(
            shortcode=self.shortcode, 
            mode="original",
        )
        self.assertEqual(deserialized_aps[0], ap1)
        self.assertEqual(deserialized_aps[1], ap2)


if __name__ == "__main__":
    unittest.main()
