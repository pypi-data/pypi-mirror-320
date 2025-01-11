# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["CriteriaInstanceCreateParams", "Body"]


class CriteriaInstanceCreateParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    answer: Required[Literal["yes", "no", "unsure"]]

    criteria_id: Required[Annotated[int, PropertyInfo(alias="criteriaId")]]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    explanation: Optional[str]
