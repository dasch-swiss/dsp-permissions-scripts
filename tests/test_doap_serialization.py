import unittest

from dsp_permissions_scripts.models import scope
from dsp_permissions_scripts.models.doap import Doap, DoapTarget
from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.utils.doap_serialize import (
    deserialize_doaps_of_project,
    serialize_doaps_of_project,
)
from tests.test_scope_serialization import compare_scopes


class TestDoapSerialization(unittest.TestCase):
    def test_doap_serialization(self):
        shortcode = "1234"

        target1 = DoapTarget(
            project="http://rdfh.ch/projects/MsOaiQkcQ7-QPxsYBKckfQ",
            group="http://www.knora.org/ontology/knora-admin#ProjectAdmin",
        )
        scope1 = scope.PermissionScope.create(
            CR=[BuiltinGroup.PROJECT_ADMIN],
            V=[BuiltinGroup.PROJECT_MEMBER],
        )
        doap1 = Doap(
            target=target1,
            scope=scope1,
            doap_iri="http://rdfh.ch/doap-1",
        )

        target2 = DoapTarget(
            project="http://rdfh.ch/projects/MsOaiQkcQ7-QPxsYBKckfQ",
            group="http://www.knora.org/ontology/knora-admin#ProjectMember",
        )
        scope2 = scope.PermissionScope.create(
            D=[BuiltinGroup.SYSTEM_ADMIN],
            M=[BuiltinGroup.KNOWN_USER],
        )
        doap2 = Doap(
            target=target2,
            scope=scope2,
            doap_iri="http://rdfh.ch/doap-2",
        )

        serialize_doaps_of_project(
            project_doaps=[doap1, doap2],
            shortcode=shortcode,
            mode="original",
        )
        deserialized_doaps = deserialize_doaps_of_project(
            shortcode=shortcode, 
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
