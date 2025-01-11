# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .protocols import (
    ProtocolsResource,
    AsyncProtocolsResource,
    ProtocolsResourceWithRawResponse,
    AsyncProtocolsResourceWithRawResponse,
    ProtocolsResourceWithStreamingResponse,
    AsyncProtocolsResourceWithStreamingResponse,
)
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["TriallyResource", "AsyncTriallyResource"]


class TriallyResource(SyncAPIResource):
    @cached_property
    def protocols(self) -> ProtocolsResource:
        return ProtocolsResource(self._client)

    @cached_property
    def with_raw_response(self) -> TriallyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return TriallyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TriallyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return TriallyResourceWithStreamingResponse(self)


class AsyncTriallyResource(AsyncAPIResource):
    @cached_property
    def protocols(self) -> AsyncProtocolsResource:
        return AsyncProtocolsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTriallyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTriallyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTriallyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncTriallyResourceWithStreamingResponse(self)


class TriallyResourceWithRawResponse:
    def __init__(self, trially: TriallyResource) -> None:
        self._trially = trially

    @cached_property
    def protocols(self) -> ProtocolsResourceWithRawResponse:
        return ProtocolsResourceWithRawResponse(self._trially.protocols)


class AsyncTriallyResourceWithRawResponse:
    def __init__(self, trially: AsyncTriallyResource) -> None:
        self._trially = trially

    @cached_property
    def protocols(self) -> AsyncProtocolsResourceWithRawResponse:
        return AsyncProtocolsResourceWithRawResponse(self._trially.protocols)


class TriallyResourceWithStreamingResponse:
    def __init__(self, trially: TriallyResource) -> None:
        self._trially = trially

    @cached_property
    def protocols(self) -> ProtocolsResourceWithStreamingResponse:
        return ProtocolsResourceWithStreamingResponse(self._trially.protocols)


class AsyncTriallyResourceWithStreamingResponse:
    def __init__(self, trially: AsyncTriallyResource) -> None:
        self._trially = trially

    @cached_property
    def protocols(self) -> AsyncProtocolsResourceWithStreamingResponse:
        return AsyncProtocolsResourceWithStreamingResponse(self._trially.protocols)
