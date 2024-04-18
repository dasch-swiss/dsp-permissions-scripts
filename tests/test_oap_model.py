import pytest

from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.errors import OapEmptyError
from dsp_permissions_scripts.models.errors import OapRetrieveConfigEmptyError
from dsp_permissions_scripts.models.errors import SpecifiedPropsEmptyError
from dsp_permissions_scripts.models.errors import SpecifiedPropsNotEmptyError
from dsp_permissions_scripts.models.errors import SpecifiedResClassesEmptyError
from dsp_permissions_scripts.models.errors import SpecifiedResClassesNotEmptyError
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_model import Oap
from dsp_permissions_scripts.oap.oap_model import OapRetrieveConfig
from dsp_permissions_scripts.oap.oap_model import ResourceOap
from dsp_permissions_scripts.oap.oap_model import ValueOap


class TestOap:
    def test_oap_one_val(self) -> None:
        res_iri = "http://rdfh.ch/0803/foo"
        scope = PermissionScope.create(D=[group.UNKNOWN_USER])
        res_oap = ResourceOap(scope=scope, resource_iri=res_iri)
        val_oaps = [
            ValueOap(
                scope=scope,
                property="foo:prop",
                value_type="foo:valtype",
                value_iri=f"{res_iri}/values/bar",
                resource_iri=res_iri,
            )
        ]
        oap = Oap(resource_oap=res_oap, value_oaps=val_oaps)
        assert oap.resource_oap == res_oap
        assert oap.value_oaps == val_oaps

    def test_oap_multiple_vals(self) -> None:
        res_iri = "http://rdfh.ch/0803/foo"
        res_scope = PermissionScope.create(D=[group.UNKNOWN_USER])
        val_scope = PermissionScope.create(M=[group.KNOWN_USER])
        res_oap = ResourceOap(scope=res_scope, resource_iri=res_iri)
        val_oap_1 = ValueOap(
            scope=val_scope,
            property="foo:prop",
            value_type="foo:valtype",
            value_iri=f"{res_iri}/values/bar",
            resource_iri=res_iri,
        )
        val_oap_2 = val_oap_1.model_copy(update={"value_iri": f"{res_iri}/values/baz"})
        oap = Oap(resource_oap=res_oap, value_oaps=[val_oap_1, val_oap_2])
        assert oap.resource_oap == res_oap
        assert oap.value_oaps == [val_oap_1, val_oap_2]

    def test_oap_no_res(self) -> None:
        res_iri = "http://rdfh.ch/0803/foo"
        scope = PermissionScope.create(D=[group.UNKNOWN_USER])
        val_oaps = [
            ValueOap(
                scope=scope,
                property="foo:prop",
                value_type="foo:valtype",
                value_iri=f"{res_iri}/values/bar",
                resource_iri=res_iri,
            )
        ]
        oap = Oap(resource_oap=None, value_oaps=val_oaps)
        assert oap.resource_oap is None
        assert oap.value_oaps == val_oaps

    def test_oap_no_res_no_vals(self) -> None:
        with pytest.raises(OapEmptyError):
            Oap(resource_oap=None, value_oaps=[])


class TestOapRetrieveConfig:
    def test_all_resources_all_values(self) -> None:
        conf = OapRetrieveConfig(retrieve_resources="all", retrieve_values="all")
        assert conf.retrieve_resources == "all"
        assert conf.specified_res_classes == []
        assert conf.retrieve_values == "all"
        assert conf.specified_props == []

    def test_all_resources_no_values(self) -> None:
        conf = OapRetrieveConfig(retrieve_resources="all", retrieve_values="none")
        assert conf.retrieve_resources == "all"
        assert conf.specified_res_classes == []
        assert conf.retrieve_values == "none"
        assert conf.specified_props == []

    def test_no_resources_all_values(self) -> None:
        conf = OapRetrieveConfig(retrieve_resources="none", retrieve_values="all")
        assert conf.retrieve_resources == "none"
        assert conf.specified_res_classes == []
        assert conf.retrieve_values == "all"
        assert conf.specified_props == []

    def test_no_resources_no_values(self) -> None:
        with pytest.raises(OapRetrieveConfigEmptyError):
            OapRetrieveConfig(retrieve_resources="none", retrieve_values="none")

    def test_all_values_but_specified(self) -> None:
        with pytest.raises(SpecifiedPropsNotEmptyError):
            OapRetrieveConfig(retrieve_values="all", specified_props=["foo"])

    def test_specified_values_but_not_specified(self) -> None:
        with pytest.raises(SpecifiedPropsEmptyError):
            OapRetrieveConfig(retrieve_values="specified_props")

    def test_no_values_but_specified(self) -> None:
        with pytest.raises(SpecifiedPropsNotEmptyError):
            OapRetrieveConfig(retrieve_values="none", specified_props=["foo"])

    def test_all_resources_but_specified(self) -> None:
        with pytest.raises(SpecifiedResClassesNotEmptyError):
            OapRetrieveConfig(retrieve_resources="all", specified_res_classes=["foo"])

    def test_no_resources_but_specified(self) -> None:
        with pytest.raises(SpecifiedResClassesNotEmptyError):
            OapRetrieveConfig(retrieve_resources="none", specified_res_classes=["foo"])

    def test_specified_resources_but_not_specified(self) -> None:
        with pytest.raises(SpecifiedResClassesEmptyError):
            OapRetrieveConfig(retrieve_resources="specified_res_classes")


if __name__ == "__main__":
    pytest.main([__file__])
