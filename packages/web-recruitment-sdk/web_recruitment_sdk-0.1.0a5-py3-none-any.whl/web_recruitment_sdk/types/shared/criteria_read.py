# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CriteriaRead"]


class CriteriaRead(BaseModel):
    id: int

    protocol_id: int = FieldInfo(alias="protocolId")

    summary: str

    type: Literal["inclusion", "exclusion"]

    description: Optional[str] = None

    status: Optional[Literal["active", "inactive"]] = None
