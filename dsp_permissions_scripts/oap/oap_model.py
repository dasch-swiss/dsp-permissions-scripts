from pydantic import BaseModel

from dsp_permissions_scripts.models.scope import PermissionScope


class Oap(BaseModel):
    """Model representing an object access permission, containing a scope and the IRI of the resource/value"""

    scope: PermissionScope
    object_iri: str
