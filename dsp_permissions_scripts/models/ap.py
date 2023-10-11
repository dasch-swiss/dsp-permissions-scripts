from pydantic import BaseModel

from dsp_permissions_scripts.models.groups import BuiltinGroup
from dsp_permissions_scripts.models.scope import PermissionScope


class Ap(BaseModel):
    forGroup: BuiltinGroup | str
    forProject: BuiltinGroup | str
    hasPermissions: PermissionScope
    iri: str
