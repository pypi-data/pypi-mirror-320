# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ProtocolFunnelStats", "CriteriaStat"]


class CriteriaStat(BaseModel):
    criteria_id: int = FieldInfo(alias="criteriaId")

    criteria_summary: str = FieldInfo(alias="criteriaSummary")

    criteria_type: Literal["inclusion", "exclusion"] = FieldInfo(alias="criteriaType")

    patients_excluded: int = FieldInfo(alias="patientsExcluded")

    patients_remaining: int = FieldInfo(alias="patientsRemaining")


class ProtocolFunnelStats(BaseModel):
    criteria_stats: List[CriteriaStat] = FieldInfo(alias="criteriaStats")

    final_matches: int = FieldInfo(alias="finalMatches")

    total_patients: int = FieldInfo(alias="totalPatients")
