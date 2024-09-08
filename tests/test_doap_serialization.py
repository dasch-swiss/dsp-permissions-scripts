import shutil
from pathlib import Path
from typing import Iterator

import pytest

from dsp_permissions_scripts.doap.doap_model import Doap
from dsp_permissions_scripts.doap.doap_model import GroupDoapTarget
from dsp_permissions_scripts.doap.doap_serialize import deserialize_doaps_of_project
from dsp_permissions_scripts.doap.doap_serialize import serialize_doaps_of_project
from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.host import Hosts
from dsp_permissions_scripts.models.scope import PermissionScope


class TestDoapSerialization:
    shortcode = "1234"

    @pytest.fixture(autouse=True)
    def _setup_teardown(self) -> Iterator[None]:
        yield
        testdata_dir = Path(f"project_data/{self.shortcode}")
        if testdata_dir.is_dir():
            shutil.rmtree(testdata_dir)

    def test_doap_serialization(self) -> None:
        doap1 = Doap(
            target=GroupDoapTarget(
                project_iri="http://rdfh.ch/projects/MsOaiQkcQ7-QPxsYBKckfQ",
                group=group.PROJECT_ADMIN,
            ),
            scope=PermissionScope.create(
                CR=[group.PROJECT_ADMIN],
                V=[group.PROJECT_MEMBER],
            ),
            doap_iri="http://rdfh.ch/doap-1",
        )
        doap2 = Doap(
            target=GroupDoapTarget(
                project_iri="http://rdfh.ch/projects/MsOaiQkcQ7-QPxsYBKckfQ",
                group=group.PROJECT_MEMBER,
            ),
            scope=PermissionScope.create(
                D=[group.SYSTEM_ADMIN],
                M=[group.KNOWN_USER],
            ),
            doap_iri="http://rdfh.ch/doap-2",
        )
        doaps_original = [doap1, doap2]
        serialize_doaps_of_project(
            project_doaps=doaps_original,
            shortcode=self.shortcode,
            mode="original",
            server=Hosts.LOCALHOST,
        )
        deserialized_doaps = deserialize_doaps_of_project(
            shortcode=self.shortcode,
            mode="original",
        )
        assert doaps_original == deserialized_doaps


if __name__ == "__main__":
    pytest.main([__file__])
