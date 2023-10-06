from pydantic import BaseModel, model_validator

from dsp_permissions_scripts.models.groups import BuiltinGroup


class PermissionScope(BaseModel, validate_assignment=True):
    """
    A scope is an object encoding the information:
    "Which user group gets which permissions on a resource/value?"
    """

    CR: frozenset[str | BuiltinGroup] = frozenset()
    D: frozenset[str | BuiltinGroup] = frozenset()
    M: frozenset[str | BuiltinGroup] = frozenset()
    V: frozenset[str | BuiltinGroup] = frozenset()
    RV: frozenset[str | BuiltinGroup] = frozenset()

    def __init__(self, **kwargs):
        kwargs_frozenset = {frozenset(x) for x in kwargs}
        super().__init__(**kwargs_frozenset)

    @model_validator(mode="after")
    def check_fields(self):
        all_groups = []
        for field in self.model_fields:
            all_groups.extend(getattr(self, field))
        for group in all_groups:
            if all_groups.count(group) > 1:
                raise ValueError(f"Group {group} must not occur in more than one field")
        return self


PUBLIC = PermissionScope(
    CR={BuiltinGroup.PROJECT_ADMIN},
    D={BuiltinGroup.CREATOR, BuiltinGroup.PROJECT_MEMBER},
    V={BuiltinGroup.UNKNOWN_USER, BuiltinGroup.KNOWN_USER},
)
