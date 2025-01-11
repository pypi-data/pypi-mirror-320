# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..shared.site_read import SiteRead

__all__ = ["Authorization", "Role"]


class Role(BaseModel):
    id: str

    description: str

    name: str


class Authorization(BaseModel):
    permissions: Optional[List[str]] = None

    role: Optional[Role] = None

    sites: Optional[List[SiteRead]] = None
