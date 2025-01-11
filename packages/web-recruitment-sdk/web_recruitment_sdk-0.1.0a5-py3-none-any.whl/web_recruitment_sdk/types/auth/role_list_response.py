# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .authress_role_read import AuthressRoleRead

__all__ = ["RoleListResponse"]

RoleListResponse: TypeAlias = List[AuthressRoleRead]
