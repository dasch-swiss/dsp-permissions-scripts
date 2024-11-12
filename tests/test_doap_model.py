import pytest

from dsp_permissions_scripts.doap.doap_model import EntityDoapTarget

SHORTCODE = "0000"
ONTO_NAME = "limc"
MY_RESCLASS_NAME = "MyResclass"
MY_PROP_NAME = ":hasProperty"
PROJ_IRI = "http://rdfh.ch/projects/P7Uo3YvDT7Kvv3EvLCl2tw"
HTTP_HOST = "http://api.dev.dasch.swiss"
HTTPS_HOST = "https://api.dev.dasch.swiss"


class TestEntityDoapTarget:
    def test_not_empty(self) -> None:
        with pytest.raises(ValueError, match="At least one of resource_class or property must be set"):
            EntityDoapTarget(project_iri=PROJ_IRI)

    def test_valid_local_class(self) -> None:
        _ = EntityDoapTarget(
            project_iri=PROJ_IRI,
            resclass_iri=f"http://0.0.0.0:3333/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_RESCLASS_NAME}",
        )

    def test_valid_local_prop(self) -> None:
        _ = EntityDoapTarget(
            project_iri=PROJ_IRI,
            property_iri=f"http://0.0.0.0:3333/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_PROP_NAME}",
        )

    def test_valid_remote_class(self) -> None:
        _ = EntityDoapTarget(
            project_iri=PROJ_IRI,
            resclass_iri=f"http://api.dev.dasch.swiss/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_RESCLASS_NAME}",
        )

    def test_valid_remote_prop(self) -> None:
        _ = EntityDoapTarget(
            project_iri=PROJ_IRI,
            property_iri=f"http://api.<subdomain>.dasch.swiss/ontology/{SHORTCODE}/{ONTO_NAME}/v2#{MY_PROP_NAME}",
        )

    def test_valid_knora_base_class(self) -> None:
        _ = EntityDoapTarget(
            project_iri=PROJ_IRI,
            resclass_iri="http://api.knora.org/ontology/knora-api/v2#StillImageRepresentation",
        )

    def test_valid_knora_base_prop(self) -> None:
        _ = EntityDoapTarget(
            project_iri=PROJ_IRI,
            property_iri="http://api.knora.org/ontology/knora-api/v2#hasValue",
        )


"http://0.0.0.0:3333/ontology/<shortcode>/<ontoname>/v2#<classname_or_property_name>"
"http://api.<subdomain>.dasch.swiss/ontology/<shortcode>/<ontoname>/v2#<classname_or_property_name>"
"http://api.knora.org/ontology/knora-api/v2#<knora_base_class_or_base_property>"
