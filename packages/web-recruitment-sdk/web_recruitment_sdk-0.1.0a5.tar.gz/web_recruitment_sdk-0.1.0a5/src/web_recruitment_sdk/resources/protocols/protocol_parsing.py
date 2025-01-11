# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.shared.protocol_parsing_read import ProtocolParsingRead

__all__ = ["ProtocolParsingResource", "AsyncProtocolParsingResource"]


class ProtocolParsingResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProtocolParsingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ProtocolParsingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProtocolParsingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ProtocolParsingResourceWithStreamingResponse(self)

    def list(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolParsingRead:
        """
        Get Protocol Parsing Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/protocols/{protocol_id}/protocol-parsing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolParsingRead,
        )


class AsyncProtocolParsingResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProtocolParsingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncProtocolParsingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProtocolParsingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncProtocolParsingResourceWithStreamingResponse(self)

    async def list(
        self,
        protocol_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolParsingRead:
        """
        Get Protocol Parsing Status

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/protocols/{protocol_id}/protocol-parsing",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolParsingRead,
        )


class ProtocolParsingResourceWithRawResponse:
    def __init__(self, protocol_parsing: ProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.list = to_raw_response_wrapper(
            protocol_parsing.list,
        )


class AsyncProtocolParsingResourceWithRawResponse:
    def __init__(self, protocol_parsing: AsyncProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.list = async_to_raw_response_wrapper(
            protocol_parsing.list,
        )


class ProtocolParsingResourceWithStreamingResponse:
    def __init__(self, protocol_parsing: ProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.list = to_streamed_response_wrapper(
            protocol_parsing.list,
        )


class AsyncProtocolParsingResourceWithStreamingResponse:
    def __init__(self, protocol_parsing: AsyncProtocolParsingResource) -> None:
        self._protocol_parsing = protocol_parsing

        self.list = async_to_streamed_response_wrapper(
            protocol_parsing.list,
        )
