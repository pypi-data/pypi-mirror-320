# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AppointmentRead"]


class AppointmentRead(BaseModel):
    id: int

    date: datetime

    patient_id: int = FieldInfo(alias="patientId")
