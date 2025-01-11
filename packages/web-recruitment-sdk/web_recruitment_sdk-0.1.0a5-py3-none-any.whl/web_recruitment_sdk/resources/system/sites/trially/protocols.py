# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.system.sites.trially.protocol_list_response import ProtocolListResponse

__all__ = ["ProtocolsResource", "AsyncProtocolsResource"]


class ProtocolsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProtocolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return ProtocolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProtocolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return ProtocolsResourceWithStreamingResponse(self)

    def list(
        self,
        trially_site_id: str,
        *,
        tenant_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolListResponse:
        """
        Get all active protocols for a site with the given trially_site_id

        Args:
          tenant_id: The tenant ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_id:
            raise ValueError(f"Expected a non-empty value for `tenant_id` but received {tenant_id!r}")
        if not trially_site_id:
            raise ValueError(f"Expected a non-empty value for `trially_site_id` but received {trially_site_id!r}")
        return self._get(
            f"/system/{tenant_id}/sites/trially/{trially_site_id}/protocols",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolListResponse,
        )


class AsyncProtocolsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProtocolsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncProtocolsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProtocolsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncProtocolsResourceWithStreamingResponse(self)

    async def list(
        self,
        trially_site_id: str,
        *,
        tenant_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolListResponse:
        """
        Get all active protocols for a site with the given trially_site_id

        Args:
          tenant_id: The tenant ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_id:
            raise ValueError(f"Expected a non-empty value for `tenant_id` but received {tenant_id!r}")
        if not trially_site_id:
            raise ValueError(f"Expected a non-empty value for `trially_site_id` but received {trially_site_id!r}")
        return await self._get(
            f"/system/{tenant_id}/sites/trially/{trially_site_id}/protocols",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolListResponse,
        )


class ProtocolsResourceWithRawResponse:
    def __init__(self, protocols: ProtocolsResource) -> None:
        self._protocols = protocols

        self.list = to_raw_response_wrapper(
            protocols.list,
        )


class AsyncProtocolsResourceWithRawResponse:
    def __init__(self, protocols: AsyncProtocolsResource) -> None:
        self._protocols = protocols

        self.list = async_to_raw_response_wrapper(
            protocols.list,
        )


class ProtocolsResourceWithStreamingResponse:
    def __init__(self, protocols: ProtocolsResource) -> None:
        self._protocols = protocols

        self.list = to_streamed_response_wrapper(
            protocols.list,
        )


class AsyncProtocolsResourceWithStreamingResponse:
    def __init__(self, protocols: AsyncProtocolsResource) -> None:
        self._protocols = protocols

        self.list = async_to_streamed_response_wrapper(
            protocols.list,
        )
