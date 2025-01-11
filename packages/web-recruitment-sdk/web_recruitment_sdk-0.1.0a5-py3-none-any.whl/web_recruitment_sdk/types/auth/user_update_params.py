# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    role_id: Annotated[
        Optional[Literal["trially-tenant-admin", "trially-site-admin", "trially-site-viewer"]],
        PropertyInfo(alias="roleId"),
    ]

    site_ids: Annotated[Optional[Iterable[int]], PropertyInfo(alias="siteIds")]
