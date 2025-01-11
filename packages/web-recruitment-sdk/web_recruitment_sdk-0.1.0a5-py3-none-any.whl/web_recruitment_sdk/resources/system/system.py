# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .patients import (
    PatientsResource,
    AsyncPatientsResource,
    PatientsResourceWithRawResponse,
    AsyncPatientsResourceWithRawResponse,
    PatientsResourceWithStreamingResponse,
    AsyncPatientsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .sites.sites import (
    SitesResource,
    AsyncSitesResource,
    SitesResourceWithRawResponse,
    AsyncSitesResourceWithRawResponse,
    SitesResourceWithStreamingResponse,
    AsyncSitesResourceWithStreamingResponse,
)
from .appointments import (
    AppointmentsResource,
    AsyncAppointmentsResource,
    AppointmentsResourceWithRawResponse,
    AsyncAppointmentsResourceWithRawResponse,
    AppointmentsResourceWithStreamingResponse,
    AsyncAppointmentsResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from .protocol_parsing import (
    ProtocolParsingResource,
    AsyncProtocolParsingResource,
    ProtocolParsingResourceWithRawResponse,
    AsyncProtocolParsingResourceWithRawResponse,
    ProtocolParsingResourceWithStreamingResponse,
    AsyncProtocolParsingResourceWithStreamingResponse,
)
from .criteria_instances import (
    CriteriaInstancesResource,
    AsyncCriteriaInstancesResource,
    CriteriaInstancesResourceWithRawResponse,
    AsyncCriteriaInstancesResourceWithRawResponse,
    CriteriaInstancesResourceWithStreamingResponse,
    AsyncCriteriaInstancesResourceWithStreamingResponse,
)
from .protocols.protocols import (
    ProtocolsResource,
    AsyncProtocolsResource,
    ProtocolsResourceWithRawResponse,
    AsyncProtocolsResourceWithRawResponse,
    ProtocolsResourceWithStreamingResponse,
    AsyncProtocolsResourceWithStreamingResponse,
)

__all__ = ["SystemResource", "AsyncSystemResource"]


class SystemResource(SyncAPIResource):
    @cached_property
    def protocols(self) -> ProtocolsResource:
        return ProtocolsResource(self._client)

    @cached_property
    def protocol_parsing(self) -> ProtocolParsingResource:
        return ProtocolParsingResource(self._client)

    @cached_property
    def sites(self) -> SitesResource:
        return SitesResource(self._client)

    @cached_property
    def appointments(self) -> AppointmentsResource:
        return AppointmentsResource(self._client)

    @cached_property
    def patients(self) -> PatientsResource:
        return PatientsResource(self._client)

    @cached_property
    def criteria_instances(self) -> CriteriaInstancesResource:
        return CriteriaInstancesResource(self._client)

    @cached_property
    def with_raw_response(self) -> SystemResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return SystemResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SystemResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return SystemResourceWithStreamingResponse(self)

    def ping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Simple health check endpoint to verify the API is running"""
        return self._get(
            "/system/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncSystemResource(AsyncAPIResource):
    @cached_property
    def protocols(self) -> AsyncProtocolsResource:
        return AsyncProtocolsResource(self._client)

    @cached_property
    def protocol_parsing(self) -> AsyncProtocolParsingResource:
        return AsyncProtocolParsingResource(self._client)

    @cached_property
    def sites(self) -> AsyncSitesResource:
        return AsyncSitesResource(self._client)

    @cached_property
    def appointments(self) -> AsyncAppointmentsResource:
        return AsyncAppointmentsResource(self._client)

    @cached_property
    def patients(self) -> AsyncPatientsResource:
        return AsyncPatientsResource(self._client)

    @cached_property
    def criteria_instances(self) -> AsyncCriteriaInstancesResource:
        return AsyncCriteriaInstancesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSystemResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return the
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSystemResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSystemResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TriallyAI/web-recruitment-sdk#with_streaming_response
        """
        return AsyncSystemResourceWithStreamingResponse(self)

    async def ping(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Simple health check endpoint to verify the API is running"""
        return await self._get(
            "/system/ping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class SystemResourceWithRawResponse:
    def __init__(self, system: SystemResource) -> None:
        self._system = system

        self.ping = to_raw_response_wrapper(
            system.ping,
        )

    @cached_property
    def protocols(self) -> ProtocolsResourceWithRawResponse:
        return ProtocolsResourceWithRawResponse(self._system.protocols)

    @cached_property
    def protocol_parsing(self) -> ProtocolParsingResourceWithRawResponse:
        return ProtocolParsingResourceWithRawResponse(self._system.protocol_parsing)

    @cached_property
    def sites(self) -> SitesResourceWithRawResponse:
        return SitesResourceWithRawResponse(self._system.sites)

    @cached_property
    def appointments(self) -> AppointmentsResourceWithRawResponse:
        return AppointmentsResourceWithRawResponse(self._system.appointments)

    @cached_property
    def patients(self) -> PatientsResourceWithRawResponse:
        return PatientsResourceWithRawResponse(self._system.patients)

    @cached_property
    def criteria_instances(self) -> CriteriaInstancesResourceWithRawResponse:
        return CriteriaInstancesResourceWithRawResponse(self._system.criteria_instances)


class AsyncSystemResourceWithRawResponse:
    def __init__(self, system: AsyncSystemResource) -> None:
        self._system = system

        self.ping = async_to_raw_response_wrapper(
            system.ping,
        )

    @cached_property
    def protocols(self) -> AsyncProtocolsResourceWithRawResponse:
        return AsyncProtocolsResourceWithRawResponse(self._system.protocols)

    @cached_property
    def protocol_parsing(self) -> AsyncProtocolParsingResourceWithRawResponse:
        return AsyncProtocolParsingResourceWithRawResponse(self._system.protocol_parsing)

    @cached_property
    def sites(self) -> AsyncSitesResourceWithRawResponse:
        return AsyncSitesResourceWithRawResponse(self._system.sites)

    @cached_property
    def appointments(self) -> AsyncAppointmentsResourceWithRawResponse:
        return AsyncAppointmentsResourceWithRawResponse(self._system.appointments)

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithRawResponse:
        return AsyncPatientsResourceWithRawResponse(self._system.patients)

    @cached_property
    def criteria_instances(self) -> AsyncCriteriaInstancesResourceWithRawResponse:
        return AsyncCriteriaInstancesResourceWithRawResponse(self._system.criteria_instances)


class SystemResourceWithStreamingResponse:
    def __init__(self, system: SystemResource) -> None:
        self._system = system

        self.ping = to_streamed_response_wrapper(
            system.ping,
        )

    @cached_property
    def protocols(self) -> ProtocolsResourceWithStreamingResponse:
        return ProtocolsResourceWithStreamingResponse(self._system.protocols)

    @cached_property
    def protocol_parsing(self) -> ProtocolParsingResourceWithStreamingResponse:
        return ProtocolParsingResourceWithStreamingResponse(self._system.protocol_parsing)

    @cached_property
    def sites(self) -> SitesResourceWithStreamingResponse:
        return SitesResourceWithStreamingResponse(self._system.sites)

    @cached_property
    def appointments(self) -> AppointmentsResourceWithStreamingResponse:
        return AppointmentsResourceWithStreamingResponse(self._system.appointments)

    @cached_property
    def patients(self) -> PatientsResourceWithStreamingResponse:
        return PatientsResourceWithStreamingResponse(self._system.patients)

    @cached_property
    def criteria_instances(self) -> CriteriaInstancesResourceWithStreamingResponse:
        return CriteriaInstancesResourceWithStreamingResponse(self._system.criteria_instances)


class AsyncSystemResourceWithStreamingResponse:
    def __init__(self, system: AsyncSystemResource) -> None:
        self._system = system

        self.ping = async_to_streamed_response_wrapper(
            system.ping,
        )

    @cached_property
    def protocols(self) -> AsyncProtocolsResourceWithStreamingResponse:
        return AsyncProtocolsResourceWithStreamingResponse(self._system.protocols)

    @cached_property
    def protocol_parsing(self) -> AsyncProtocolParsingResourceWithStreamingResponse:
        return AsyncProtocolParsingResourceWithStreamingResponse(self._system.protocol_parsing)

    @cached_property
    def sites(self) -> AsyncSitesResourceWithStreamingResponse:
        return AsyncSitesResourceWithStreamingResponse(self._system.sites)

    @cached_property
    def appointments(self) -> AsyncAppointmentsResourceWithStreamingResponse:
        return AsyncAppointmentsResourceWithStreamingResponse(self._system.appointments)

    @cached_property
    def patients(self) -> AsyncPatientsResourceWithStreamingResponse:
        return AsyncPatientsResourceWithStreamingResponse(self._system.patients)

    @cached_property
    def criteria_instances(self) -> AsyncCriteriaInstancesResourceWithStreamingResponse:
        return AsyncCriteriaInstancesResourceWithStreamingResponse(self._system.criteria_instances)
