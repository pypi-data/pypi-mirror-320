# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["CriterionUpdateParams"]


class CriterionUpdateParams(TypedDict, total=False):
    description: Optional[str]

    status: Optional[Literal["active", "inactive"]]

    summary: Optional[str]
