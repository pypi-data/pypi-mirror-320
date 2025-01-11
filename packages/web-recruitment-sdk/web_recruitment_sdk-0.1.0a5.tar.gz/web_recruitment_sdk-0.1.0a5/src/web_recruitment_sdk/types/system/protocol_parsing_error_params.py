# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["ProtocolParsingErrorParams"]


class ProtocolParsingErrorParams(TypedDict, total=False):
    tenant_id: Required[str]
    """The tenant ID"""

    status_message: Optional[str]
