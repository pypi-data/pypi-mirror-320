# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["PatientBulkProceduresParams", "Body"]


class PatientBulkProceduresParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    cui: Required[str]

    name: Required[str]

    trially_patient_id: Required[Annotated[str, PropertyInfo(alias="triallyPatientId")]]

    trially_procedure_id: Required[Annotated[str, PropertyInfo(alias="triallyProcedureId")]]

    date_started: Annotated[Union[str, datetime, None], PropertyInfo(alias="dateStarted", format="iso8601")]
