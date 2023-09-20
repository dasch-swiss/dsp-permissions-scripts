from pydantic import BaseModel, root_validator, validator

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScopeElement(BaseModel):
    info: str | BuiltinGroup
    name: str

    @validator("info")
    @classmethod
    def info_must_represent_group_iri(cls, v: str | BuiltinGroup) -> str | BuiltinGroup:
        assert v in [x.value for x in BuiltinGroup]
        return v

    @validator("name")
    @classmethod
    def name_must_represent_permission(cls, v: str) -> str:
        assert v in {"RV", "V", "M", "D", "CR"}
        return v


class DoapTarget(BaseModel):
    project: str
    group: str | None
    resource_class: str | None
    property: str | None

    @root_validator
    @classmethod
    def assert_correct_combination(cls, values: dict[str, str | None]) -> dict[str, str | None]:
        # asserts that DOAP is only defined for Group or ResourceClass or Property
        # or a combination of ResourceClass and Property
        match (values["group"], values["resource_class"], values["property"]):
            case (None, None, None):
                raise ValueError("At least one of group, resource_class or property must be set")
            case (_, None, None) | (None, _, _):
                pass
            case _:
                raise ValueError("Invalid combination of group, resource_class and property")
        return values


class Doap(BaseModel):
    """
    Model representing a DOAP, containing the target, the scope and the IRI of the DOAP.
    """

    target: DoapTarget
    scope: list[PermissionScopeElement]
    iri: str
