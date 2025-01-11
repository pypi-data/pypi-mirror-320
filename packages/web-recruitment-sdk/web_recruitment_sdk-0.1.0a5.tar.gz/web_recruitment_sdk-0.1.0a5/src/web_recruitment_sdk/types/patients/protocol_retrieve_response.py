# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from ..shared.patient_read import PatientRead

__all__ = ["ProtocolRetrieveResponse"]

ProtocolRetrieveResponse: TypeAlias = List[PatientRead]
