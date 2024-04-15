import shutil
import unittest
from pathlib import Path

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_model import Oap, ValueOap
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_serialize import deserialize_oaps
from dsp_permissions_scripts.oap.oap_serialize import serialize_oaps
from tests.test_scope_serialization import compare_scopes


class TestOapSerialization(unittest.TestCase):
    shortcode = "1234"

    def tearDown(self) -> None:
        testdata_dir = Path(f"project_data/{self.shortcode}")
        if testdata_dir.is_dir():
            shutil.rmtree(testdata_dir)

    def test_oap_serialization(self) -> None:
        oap1 = self._get_oap_full()
        oap2 = self._get_oap_one_value_only()
        oap3 = self._get_oap_res_only()

        serialize_oaps([oap1, oap2, oap3], self.shortcode, "original")
        deserialized_oaps = deserialize_oaps(self.shortcode, "original")
        self._compare_oaps(deserialized_oaps[0], oap1)
        self._compare_oaps(deserialized_oaps[1], oap2)
        self._compare_oaps(deserialized_oaps[2], oap3)

    def _get_oap_full(self) -> Oap:
        scope = PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.PROJECT_MEMBER])
        res_iri = f"http://rdfh.ch/{self.shortcode}/resource-1"
        res_oap = ResourceOap(scope=scope, resource_iri=res_iri)
        val1_oap = ValueOap(
            scope=scope, 
            property="foo:prop1", 
            value_type="bar:val1", 
            value_iri=f"{res_iri}/values/foobar1", 
            resource_iri=res_iri
        )
        val2_oap = ValueOap(
            scope=scope, 
            property="foo:prop2", 
            value_type="bar:val2", 
            value_iri=f"{res_iri}/values/foobar2", 
            resource_iri=res_iri
        )
        oap = Oap(resource_oap=res_oap, value_oaps=[val1_oap, val2_oap])
        return oap
    
    def _get_oap_one_value_only(self) -> Oap:
        scope = PermissionScope.create(D=[group.SYSTEM_ADMIN], M=[group.KNOWN_USER])
        res_iri = f"http://rdfh.ch/{self.shortcode}/resource-2"
        val_oap = ValueOap(
            scope=scope, 
            property="foo:prop3", 
            value_type="bar:val3", 
            value_iri=f"{res_iri}/values/foobar3", 
            resource_iri=res_iri
        )
        return Oap(resource_oap=None, value_oaps=[val_oap])
    
    def _get_oap_res_only(self) -> Oap:
        scope = PermissionScope.create(V=[group.KNOWN_USER], RV=[group.UNKNOWN_USER])
        res_iri = f"http://rdfh.ch/{self.shortcode}/resource-3"
        res_oap = ResourceOap(scope=scope, resource_iri=res_iri)
        return Oap(resource_oap=res_oap, value_oaps=[])

    def _compare_oaps(self, oap1: Oap, oap2: Oap) -> None:
        if oap1.resource_oap is None:
            self.assertIsNone(oap2.resource_oap)
        if oap2.resource_oap is None:
            self.assertIsNone(oap1.resource_oap)
        self.assertEqual(oap1.resource_oap.resource_iri, oap2.resource_oap.resource_iri)
        compare_scopes(oap1.resource_oap.scope, oap2.resource_oap.scope)

        self.assertEqual(len(oap1.value_oaps), len(oap2.value_oaps))
        for val_oap1, val_oap2 in zip(oap1.value_oaps, oap2.value_oaps):
            self.assertEqual(val_oap1.value_iri, val_oap2.value_iri)
            self.assertEqual(val_oap1.property, val_oap2.property)
            self.assertEqual(val_oap1.value_type, val_oap2.value_type)
            compare_scopes(val_oap1.scope, val_oap2.scope)


if __name__ == "__main__":
    unittest.main()
