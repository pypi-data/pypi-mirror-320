# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["CriterionCreateParams"]


class CriterionCreateParams(TypedDict, total=False):
    protocol_id: Required[Annotated[int, PropertyInfo(alias="protocolId")]]

    summary: Required[str]

    type: Required[Literal["inclusion", "exclusion"]]

    description: Optional[str]

    status: Literal["active", "inactive"]
