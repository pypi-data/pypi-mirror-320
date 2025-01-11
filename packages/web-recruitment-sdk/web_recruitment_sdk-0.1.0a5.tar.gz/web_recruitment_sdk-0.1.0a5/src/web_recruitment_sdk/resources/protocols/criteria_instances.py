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
from ...types.protocols import criteria_instance_list_params
from ...types.protocols.criteria_instance_list_response import CriteriaInstanceListResponse

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

    def list(
        self,
        protocol_id: int,
        *,
        trially_patient_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriteriaInstanceListResponse:
        """
        Get Criteria Instances

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/protocols/{protocol_id}/criteria_instances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"trially_patient_id": trially_patient_id}, criteria_instance_list_params.CriteriaInstanceListParams
                ),
            ),
            cast_to=CriteriaInstanceListResponse,
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

    async def list(
        self,
        protocol_id: int,
        *,
        trially_patient_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CriteriaInstanceListResponse:
        """
        Get Criteria Instances

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/protocols/{protocol_id}/criteria_instances",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"trially_patient_id": trially_patient_id}, criteria_instance_list_params.CriteriaInstanceListParams
                ),
            ),
            cast_to=CriteriaInstanceListResponse,
        )


class CriteriaInstancesResourceWithRawResponse:
    def __init__(self, criteria_instances: CriteriaInstancesResource) -> None:
        self._criteria_instances = criteria_instances

        self.list = to_raw_response_wrapper(
            criteria_instances.list,
        )


class AsyncCriteriaInstancesResourceWithRawResponse:
    def __init__(self, criteria_instances: AsyncCriteriaInstancesResource) -> None:
        self._criteria_instances = criteria_instances

        self.list = async_to_raw_response_wrapper(
            criteria_instances.list,
        )


class CriteriaInstancesResourceWithStreamingResponse:
    def __init__(self, criteria_instances: CriteriaInstancesResource) -> None:
        self._criteria_instances = criteria_instances

        self.list = to_streamed_response_wrapper(
            criteria_instances.list,
        )


class AsyncCriteriaInstancesResourceWithStreamingResponse:
    def __init__(self, criteria_instances: AsyncCriteriaInstancesResource) -> None:
        self._criteria_instances = criteria_instances

        self.list = async_to_streamed_response_wrapper(
            criteria_instances.list,
        )
