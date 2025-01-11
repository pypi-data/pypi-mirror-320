# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["AppointmentBulkParams", "Body"]


class AppointmentBulkParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    date: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]

    patient_id: Required[Annotated[int, PropertyInfo(alias="patientId")]]
