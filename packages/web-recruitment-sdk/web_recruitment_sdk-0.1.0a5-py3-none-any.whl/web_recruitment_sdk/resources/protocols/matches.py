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
from ...types.protocols.match_list_response import MatchListResponse

__all__ = ["MatchesResource", "AsyncMatchesResource"]


class MatchesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MatchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return MatchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MatchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return MatchesResourceWithStreamingResponse(self)

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
    ) -> MatchListResponse:
        """
        Get Protocol Matches

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/protocols/{protocol_id}/matches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchListResponse,
        )


class AsyncMatchesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMatchesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMatchesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMatchesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncMatchesResourceWithStreamingResponse(self)

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
    ) -> MatchListResponse:
        """
        Get Protocol Matches

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/protocols/{protocol_id}/matches",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MatchListResponse,
        )


class MatchesResourceWithRawResponse:
    def __init__(self, matches: MatchesResource) -> None:
        self._matches = matches

        self.list = to_raw_response_wrapper(
            matches.list,
        )


class AsyncMatchesResourceWithRawResponse:
    def __init__(self, matches: AsyncMatchesResource) -> None:
        self._matches = matches

        self.list = async_to_raw_response_wrapper(
            matches.list,
        )


class MatchesResourceWithStreamingResponse:
    def __init__(self, matches: MatchesResource) -> None:
        self._matches = matches

        self.list = to_streamed_response_wrapper(
            matches.list,
        )


class AsyncMatchesResourceWithStreamingResponse:
    def __init__(self, matches: AsyncMatchesResource) -> None:
        self._matches = matches

        self.list = async_to_streamed_response_wrapper(
            matches.list,
        )
