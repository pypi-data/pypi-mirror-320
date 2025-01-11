# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["UserCreateParams"]


class UserCreateParams(TypedDict, total=False):
    email: Required[str]

    role_id: Required[
        Annotated[
            Literal["trially-tenant-admin", "trially-site-admin", "trially-site-viewer"], PropertyInfo(alias="roleId")
        ]
    ]
    """The role name in Authress"""

    site_ids: Annotated[Iterable[int], PropertyInfo(alias="siteIds")]
    """Sites the user will have access to"""
