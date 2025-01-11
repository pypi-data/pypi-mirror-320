# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.patients import protocol_retrieve_params
from ...types.patients.protocol_retrieve_response import ProtocolRetrieveResponse

__all__ = ["ProtocolResource", "AsyncProtocolResource"]


class ProtocolResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProtocolResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ProtocolResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProtocolResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ProtocolResourceWithStreamingResponse(self)

    def retrieve(
        self,
        protocol_id: int,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRetrieveResponse:
        """
        Get Patients By Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/patients/protocol/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"limit": limit}, protocol_retrieve_params.ProtocolRetrieveParams),
            ),
            cast_to=ProtocolRetrieveResponse,
        )


class AsyncProtocolResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProtocolResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncProtocolResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProtocolResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncProtocolResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        protocol_id: int,
        *,
        limit: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRetrieveResponse:
        """
        Get Patients By Protocol

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/patients/protocol/{protocol_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"limit": limit}, protocol_retrieve_params.ProtocolRetrieveParams),
            ),
            cast_to=ProtocolRetrieveResponse,
        )


class ProtocolResourceWithRawResponse:
    def __init__(self, protocol: ProtocolResource) -> None:
        self._protocol = protocol

        self.retrieve = to_raw_response_wrapper(
            protocol.retrieve,
        )


class AsyncProtocolResourceWithRawResponse:
    def __init__(self, protocol: AsyncProtocolResource) -> None:
        self._protocol = protocol

        self.retrieve = async_to_raw_response_wrapper(
            protocol.retrieve,
        )


class ProtocolResourceWithStreamingResponse:
    def __init__(self, protocol: ProtocolResource) -> None:
        self._protocol = protocol

        self.retrieve = to_streamed_response_wrapper(
            protocol.retrieve,
        )


class AsyncProtocolResourceWithStreamingResponse:
    def __init__(self, protocol: AsyncProtocolResource) -> None:
        self._protocol = protocol

        self.retrieve = async_to_streamed_response_wrapper(
            protocol.retrieve,
        )
