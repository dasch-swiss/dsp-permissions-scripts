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
        scope1 = PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.PROJECT_MEMBER])
        res_iri1 = f"http://rdfh.ch/{self.shortcode}/resource-1"
        res_oap1 = ResourceOap(scope=scope1, resource_iri=res_iri1)
        val_iri1_1 = f"{res_iri1}/values/foobar1"
        val_oap1_1 = ValueOap(
            scope=scope1, property="foo:bar", value_type="bar:baz", value_iri=val_iri1_1, resource_iri=res_iri1
        )
        val_iri1_2 = f"{res_iri1}/values/foobar2"
        val_oap1_2 = ValueOap(
            scope=scope1, property="foo:bar", value_type="bar:baz", value_iri=val_iri1_2, resource_iri=res_iri1
        )
        oap1 = Oap(resource_oap=res_oap1, value_oaps=[val_oap1_1, val_oap1_2])

        scope2 = PermissionScope.create(D=[group.SYSTEM_ADMIN], M=[group.KNOWN_USER])
        res_iri2 = f"http://rdfh.ch/{self.shortcode}/resource-2"
        res_oap2 = ResourceOap(scope=scope2, resource_iri=res_iri2)
        val_iri2_1 = f"{res_iri2}/values/foobar1"
        val_oap2_1 = ValueOap(
            scope=scope2, property="foo:bar", value_type="bar:baz", value_iri=val_iri2_1, resource_iri=res_iri2
        )
        val_iri2_2 = f"{res_iri2}/values/foobar2"
        val_oap2_2 = ValueOap(
            scope=scope2, property="foo:bar", value_type="bar:baz", value_iri=val_iri2_2, resource_iri=res_iri2
        )
        oap2 = Oap(resource_oap=res_oap2, value_oaps=[val_oap2_1, val_oap2_2])

        serialize_oaps([oap1, oap2], self.shortcode, "original")
        deserialized_oaps = deserialize_oaps(self.shortcode, "original")
        self._compare_oaps(deserialized_oaps[0], oap1)
        self._compare_oaps(deserialized_oaps[1], oap2)

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
