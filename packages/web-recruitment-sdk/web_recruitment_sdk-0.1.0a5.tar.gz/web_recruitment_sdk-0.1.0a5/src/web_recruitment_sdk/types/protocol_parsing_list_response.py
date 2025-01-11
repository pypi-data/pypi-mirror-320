# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import TypeAlias

from .shared.protocol_parsing_read import ProtocolParsingRead

__all__ = ["ProtocolParsingListResponse"]

ProtocolParsingListResponse: TypeAlias = List[ProtocolParsingRead]
