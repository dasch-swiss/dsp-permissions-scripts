from dsp_permissions_scripts.models import group
from dsp_permissions_scripts.models.scope import PermissionScope
from dsp_permissions_scripts.oap.oap_get import _get_value_oaps
from dsp_permissions_scripts.oap.oap_model import ValueOap


def test_oap_get_multiple_values_per_prop() -> None:
    resource = {
        "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        "geoarch:hasDescriptionSiteProject": {
            "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|V knora-admin:KnownUser,knora-admin:UnknownUser",
            "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/o0313dsSQTSPGua4NSWkeQ",
            "@type": "knora-api:TextValue",
        },
        "geoarch:hasFurtherDisciplines": [
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|M knora-admin:ProjectMember",
                "@type": "knora-api:ListValue",
                "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/ZC-1hUiMR0mVXdaCBg1jsA",
            },
            {
                "knora-api:hasPermissions": "CR knora-admin:ProjectAdmin|M knora-admin:ProjectMember",
                "@type": "knora-api:ListValue",
                "@id": "http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/FMJ3-eUARl-shQ6ZbUn9aw",
            },
        ],
    }
    expected = [
        ValueOap(
            scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], V=[group.KNOWN_USER, group.UNKNOWN_USER]),
            property="geoarch:hasDescriptionSiteProject",
            value_type="knora-api:TextValue",
            value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/o0313dsSQTSPGua4NSWkeQ",
            resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        ),
        ValueOap(
            scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], M=[group.PROJECT_MEMBER]),
            property="geoarch:hasFurtherDisciplines",
            value_type="knora-api:ListValue",
            value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/ZC-1hUiMR0mVXdaCBg1jsA",
            resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        ),
        ValueOap(
            scope=PermissionScope.create(CR=[group.PROJECT_ADMIN], M=[group.PROJECT_MEMBER]),
            property="geoarch:hasFurtherDisciplines",
            value_type="knora-api:ListValue",
            value_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q/values/FMJ3-eUARl-shQ6ZbUn9aw",
            resource_iri="http://rdfh.ch/0838/dBu563hjSN6RmJZp6NU3_Q",
        ),
    ]
    returned = _get_value_oaps(resource)
    assert expected == returned
