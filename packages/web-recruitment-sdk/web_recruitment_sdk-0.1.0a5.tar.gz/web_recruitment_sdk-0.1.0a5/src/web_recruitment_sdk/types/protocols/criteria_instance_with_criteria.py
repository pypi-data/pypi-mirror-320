# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CriteriaInstanceWithCriteria"]


class CriteriaInstanceWithCriteria(BaseModel):
    id: int

    answer: Literal["yes", "no", "unsure"]

    criteria_id: int = FieldInfo(alias="criteriaId")

    criteria_summary: str = FieldInfo(alias="criteriaSummary")

    criteria_type: Literal["inclusion", "exclusion"] = FieldInfo(alias="criteriaType")

    trially_patient_id: str = FieldInfo(alias="triallyPatientId")

    explanation: Optional[str] = None
