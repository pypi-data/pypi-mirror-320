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
from ...types.system import criteria_instance_create_params
from ...types.system.criteria_instance_create_response import CriteriaInstanceCreateResponse

__all__ = ["CriteriaInstancesResource", "AsyncCriteriaInstancesResource"]


class CriteriaInstancesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CriteriaInstancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return CriteriaInstancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CriteriaInstancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return CriteriaInstancesResourceWithStreamingResponse(self)

    def create(
        self,
        tenant_id: str,
        *,
        body: Iterable[criteria_instance_create_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriteriaInstanceCreateResponse:
        """
        Create Criteria Instances

        Args:
          tenant_id: The tenant ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_id:
            raise ValueError(f"Expected a non-empty value for `tenant_id` but received {tenant_id!r}")
        return self._post(
            f"/system/{tenant_id}/criteria_instances",
            body=maybe_transform(body, Iterable[criteria_instance_create_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaInstanceCreateResponse,
        )


class AsyncCriteriaInstancesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCriteriaInstancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCriteriaInstancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCriteriaInstancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncCriteriaInstancesResourceWithStreamingResponse(self)

    async def create(
        self,
        tenant_id: str,
        *,
        body: Iterable[criteria_instance_create_params.Body],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriteriaInstanceCreateResponse:
        """
        Create Criteria Instances

        Args:
          tenant_id: The tenant ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not tenant_id:
            raise ValueError(f"Expected a non-empty value for `tenant_id` but received {tenant_id!r}")
        return await self._post(
            f"/system/{tenant_id}/criteria_instances",
            body=await async_maybe_transform(body, Iterable[criteria_instance_create_params.Body]),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CriteriaInstanceCreateResponse,
        )


class CriteriaInstancesResourceWithRawResponse:
    def __init__(self, criteria_instances: CriteriaInstancesResource) -> None:
        self._criteria_instances = criteria_instances

        self.create = to_raw_response_wrapper(
            criteria_instances.create,
        )


class AsyncCriteriaInstancesResourceWithRawResponse:
    def __init__(self, criteria_instances: AsyncCriteriaInstancesResource) -> None:
        self._criteria_instances = criteria_instances

        self.create = async_to_raw_response_wrapper(
            criteria_instances.create,
        )


class CriteriaInstancesResourceWithStreamingResponse:
    def __init__(self, criteria_instances: CriteriaInstancesResource) -> None:
        self._criteria_instances = criteria_instances

        self.create = to_streamed_response_wrapper(
            criteria_instances.create,
        )


class AsyncCriteriaInstancesResourceWithStreamingResponse:
    def __init__(self, criteria_instances: AsyncCriteriaInstancesResource) -> None:
        self._criteria_instances = criteria_instances

        self.create = async_to_streamed_response_wrapper(
            criteria_instances.create,
        )
