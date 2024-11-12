import pytest

from dsp_permissions_scripts.doap.doap_model import EntityDoapTarget
from dsp_permissions_scripts.doap.doap_model import NewEntityDoapTarget
from dsp_permissions_scripts.models.errors import EmptyDoapTargetError

SHORTCODE = "0000"
ONTO_NAME = "limc"
MY_RESCLASS_NAME = "MyResclass"
MY_PROP_NAME = ":hasProperty"
PROJ_IRI = "http://rdfh.ch/projects/P7Uo3YvDT7Kvv3EvLCl2tw"
HTTP_HOST = "http://api.dev.dasch.swiss"
HTTPS_HOST = "https://api.dev.dasch.swiss"

RESCLASS_LOCAL = f"http://0.0.0.0:3333/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_RESCLASS_NAME}"
PROP_LOCAL = f"http://0.0.0.0:3333/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_PROP_NAME}"

RESCLASS_REMOTE = f"http://api.rdu-14.dasch.swiss/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_RESCLASS_NAME}"
PROP_REMOTE = f"http://api.dasch.swiss/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_PROP_NAME}"

RESCLASS_KNORA_BASE = "http://api.knora.org/ontology/knora-api/v2#StillImageRepresentation"
PROP_KNORA_BASE = "http://api.knora.org/ontology/knora-api/v2#hasValue"


class TestEntityDoapTarget:
    def test_not_empty(self) -> None:
        with pytest.raises(EmptyDoapTargetError):
            EntityDoapTarget(project_iri=PROJ_IRI)

    @pytest.mark.parametrize(
        ("resclass", "prop"), [(RESCLASS_LOCAL, PROP_LOCAL), (RESCLASS_LOCAL, None), (None, PROP_LOCAL)]
    )
    def test_valid_local(self, resclass: str | None, prop: str | None) -> None:
        _ = EntityDoapTarget(project_iri=PROJ_IRI, resclass_iri=resclass, property_iri=prop)

    @pytest.mark.parametrize(
        ("resclass", "prop"), [(RESCLASS_REMOTE, PROP_REMOTE), (RESCLASS_REMOTE, None), (None, PROP_REMOTE)]
    )
    def test_valid_remote(self, resclass: str | None, prop: str | None) -> None:
        _ = EntityDoapTarget(project_iri=PROJ_IRI, resclass_iri=resclass, property_iri=prop)

    @pytest.mark.parametrize(
        ("resclass", "prop"),
        [(RESCLASS_KNORA_BASE, PROP_KNORA_BASE), (RESCLASS_KNORA_BASE, None), (None, PROP_KNORA_BASE)],
    )
    def test_valid_knora_base(self, resclass: str | None, prop: str | None) -> None:
        _ = EntityDoapTarget(project_iri=PROJ_IRI, resclass_iri=resclass, property_iri=prop)

    @pytest.mark.parametrize(
        "inv",
        [
            "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWxg/values/eD0ii5mIS9y18M6fMy1Fk",
            "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWxg",
            MY_RESCLASS_NAME,
            MY_PROP_NAME,
            PROJ_IRI,
            HTTP_HOST,
        ],
    )
    def test_invalid(self, inv: str) -> None:
        with pytest.raises(ValueError, match="IRI must be in one of the formats"):
            _ = EntityDoapTarget(project_iri=PROJ_IRI, resclass_iri=inv)
        with pytest.raises(ValueError, match="IRI must be in one of the formats"):
            _ = EntityDoapTarget(project_iri=PROJ_IRI, property_iri=inv)


class TestNewEntityDoapTarget:
    def test_not_empty(self) -> None:
        with pytest.raises(EmptyDoapTargetError):
            NewEntityDoapTarget()

    @pytest.mark.parametrize(
        ("resclass", "prop"), [("My-Onto:My-Class", "my_onto:prop_name"), ("onto:class", None), (None, "onto-1:prop-1")]
    )
    def test_valid(self, resclass: str | None, prop: str | None) -> None:
        _ = NewEntityDoapTarget(prefixed_class=resclass, prefixed_prop=prop)

    @pytest.mark.parametrize(
        "inv",
        [
            RESCLASS_LOCAL,
            PROP_LOCAL,
            RESCLASS_REMOTE,
            PROP_REMOTE,
            RESCLASS_KNORA_BASE,
            PROP_KNORA_BASE,
            "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWxg/values/eD0ii5mIS9y18M6fMy1Fk",
            "http://rdfh.ch/4123/CPm__dQhRoKPzvjzrPuWxg",
            MY_RESCLASS_NAME,
            MY_PROP_NAME,
            PROJ_IRI,
            HTTP_HOST,
        ],
    )
    def test_invalid(self, inv: str) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _ = NewEntityDoapTarget(prefixed_class=inv)
        with pytest.raises(ValueError):  # noqa: PT011
            _ = NewEntityDoapTarget(prefixed_prop=inv)
