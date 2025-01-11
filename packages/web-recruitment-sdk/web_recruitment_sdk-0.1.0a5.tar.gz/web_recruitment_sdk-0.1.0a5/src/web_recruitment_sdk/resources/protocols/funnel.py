# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

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
from ...types.protocols import funnel_retrieve_params
from ...types.protocols.protocol_funnel_stats import ProtocolFunnelStats

__all__ = ["FunnelResource", "AsyncFunnelResource"]


class FunnelResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FunnelResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return FunnelResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FunnelResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return FunnelResourceWithStreamingResponse(self)

    def retrieve(
        self,
        protocol_id: int,
        *,
        site_ids: Iterable[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolFunnelStats:
        """
        Get Protocol Funnel

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/protocols/{protocol_id}/funnel",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"site_ids": site_ids}, funnel_retrieve_params.FunnelRetrieveParams),
            ),
            cast_to=ProtocolFunnelStats,
        )


class AsyncFunnelResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFunnelResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncFunnelResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFunnelResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncFunnelResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        protocol_id: int,
        *,
        site_ids: Iterable[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolFunnelStats:
        """
        Get Protocol Funnel

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/protocols/{protocol_id}/funnel",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"site_ids": site_ids}, funnel_retrieve_params.FunnelRetrieveParams),
            ),
            cast_to=ProtocolFunnelStats,
        )


class FunnelResourceWithRawResponse:
    def __init__(self, funnel: FunnelResource) -> None:
        self._funnel = funnel

        self.retrieve = to_raw_response_wrapper(
            funnel.retrieve,
        )


class AsyncFunnelResourceWithRawResponse:
    def __init__(self, funnel: AsyncFunnelResource) -> None:
        self._funnel = funnel

        self.retrieve = async_to_raw_response_wrapper(
            funnel.retrieve,
        )


class FunnelResourceWithStreamingResponse:
    def __init__(self, funnel: FunnelResource) -> None:
        self._funnel = funnel

        self.retrieve = to_streamed_response_wrapper(
            funnel.retrieve,
        )


class AsyncFunnelResourceWithStreamingResponse:
    def __init__(self, funnel: AsyncFunnelResource) -> None:
        self._funnel = funnel

        self.retrieve = async_to_streamed_response_wrapper(
            funnel.retrieve,
        )
