from pydantic import BaseModel, root_validator, validator


class PermissionScope(BaseModel):
    info: str
    name: str

    @validator("name")
    def name_must_represent_permission(cls, v: str) -> str:
        assert v in {"RV", "V", "M", "D", "CR"}
        return v


class DoapTarget(BaseModel):
    project: str
    group: str | None
    resource_class: str | None
    property: str | None

    @root_validator
    def assert_correct_combination(cls, values: dict[str, str | None]) -> dict[str, str | None]:
        match (values["group"], values["resource_class"], values["property"]):
            case (None, None, None):
                raise ValueError("At least one of group, resource_class or property must be set")
            case (_, None, None) | (None, _, _):
                pass
            case _:
                raise ValueError("Invalid combination of group, resource_class and property")
        return values


class Doap(BaseModel):
    target: DoapTarget
    scope: list[PermissionScope]
    iri: str
