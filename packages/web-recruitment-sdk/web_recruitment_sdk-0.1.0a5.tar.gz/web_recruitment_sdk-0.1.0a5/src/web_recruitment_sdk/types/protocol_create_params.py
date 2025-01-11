# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ProtocolCreateParams"]


class ProtocolCreateParams(TypedDict, total=False):
    external_protocol_id: Required[Annotated[Optional[str], PropertyInfo(alias="externalProtocolId")]]

    title: Required[str]

    version: int
