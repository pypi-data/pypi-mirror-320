# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AuthressRoleRead"]


class AuthressRoleRead(BaseModel):
    id: Literal["trially-tenant-admin", "trially-site-admin", "trially-site-viewer"]

    name: str

    description: Optional[str] = None
