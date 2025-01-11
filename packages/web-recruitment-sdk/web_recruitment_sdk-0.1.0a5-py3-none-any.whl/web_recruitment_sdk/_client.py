# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, Union, Mapping, Iterable, cast
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from .types import client_protocol_parsing_params
from ._types import (
    NOT_GIVEN,
    Body,
    Omit,
    Query,
    Headers,
    Timeout,
    NotGiven,
    FileTypes,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import (
    is_given,
    maybe_transform,
    get_async_library,
    async_maybe_transform,
)
from ._version import __version__
from ._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .resources import sites, health, criteria, appointments, feature_flags, protocol_parsings, patients_by_external_id
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, WebRecruitmentSDKError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
    make_request_options,
)
from .resources.auth import auth
from .resources.admin import admin
from .resources.system import system
from .resources.patients import patients
from .resources.protocols import protocols
from .types.shared.protocol_read import ProtocolRead

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "WebRecruitmentSDK",
    "AsyncWebRecruitmentSDK",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "production": "https://trially-backend-production-861990824910.us-central1.run.app",
    "staging": "https://trially-backend-staging-965051512294.us-central1.run.app",
}


class WebRecruitmentSDK(SyncAPIClient):
    auth: auth.AuthResource
    admin: admin.AdminResource
    patients: patients.PatientsResource
    patients_by_external_id: patients_by_external_id.PatientsByExternalIDResource
    protocols: protocols.ProtocolsResource
    protocol_parsings: protocol_parsings.ProtocolParsingsResource
    criteria: criteria.CriteriaResource
    appointments: appointments.AppointmentsResource
    sites: sites.SitesResource
    health: health.HealthResource
    system: system.SystemResource
    feature_flags: feature_flags.FeatureFlagsResource
    with_raw_response: WebRecruitmentSDKWithRawResponse
    with_streaming_response: WebRecruitmentSDKWithStreamedResponse

    # client options
    bearer_token: str

    _environment: Literal["production", "staging"] | NotGiven

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        environment: Literal["production", "staging"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous web-recruitment-sdk client instance.

        This automatically infers the `bearer_token` argument from the `BEARER_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("BEARER_TOKEN")
        if bearer_token is None:
            raise WebRecruitmentSDKError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the BEARER_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        self._environment = environment

        base_url_env = os.environ.get("WEB_RECRUITMENT_SDK_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `WEB_RECRUITMENT_SDK_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.auth = auth.AuthResource(self)
        self.admin = admin.AdminResource(self)
        self.patients = patients.PatientsResource(self)
        self.patients_by_external_id = patients_by_external_id.PatientsByExternalIDResource(self)
        self.protocols = protocols.ProtocolsResource(self)
        self.protocol_parsings = protocol_parsings.ProtocolParsingsResource(self)
        self.criteria = criteria.CriteriaResource(self)
        self.appointments = appointments.AppointmentsResource(self)
        self.sites = sites.SitesResource(self)
        self.health = health.HealthResource(self)
        self.system = system.SystemResource(self)
        self.feature_flags = feature_flags.FeatureFlagsResource(self)
        self.with_raw_response = WebRecruitmentSDKWithRawResponse(self)
        self.with_streaming_response = WebRecruitmentSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        environment: Literal["production", "staging"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def protocol_parsing(
        self,
        *,
        file: FileTypes,
        title: str,
        site_ids: Iterable[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Upload Protocol

        Args:
          file: The protocol file to upload

          title: The title of the protocol

          site_ids: The site IDs to associate with the protocol

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self.post(
            "/protocol-parsing",
            body=maybe_transform(
                {
                    "file": file,
                    "title": title,
                    "site_ids": site_ids,
                },
                client_protocol_parsing_params.ClientProtocolParsingParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncWebRecruitmentSDK(AsyncAPIClient):
    auth: auth.AsyncAuthResource
    admin: admin.AsyncAdminResource
    patients: patients.AsyncPatientsResource
    patients_by_external_id: patients_by_external_id.AsyncPatientsByExternalIDResource
    protocols: protocols.AsyncProtocolsResource
    protocol_parsings: protocol_parsings.AsyncProtocolParsingsResource
    criteria: criteria.AsyncCriteriaResource
    appointments: appointments.AsyncAppointmentsResource
    sites: sites.AsyncSitesResource
    health: health.AsyncHealthResource
    system: system.AsyncSystemResource
    feature_flags: feature_flags.AsyncFeatureFlagsResource
    with_raw_response: AsyncWebRecruitmentSDKWithRawResponse
    with_streaming_response: AsyncWebRecruitmentSDKWithStreamedResponse

    # client options
    bearer_token: str

    _environment: Literal["production", "staging"] | NotGiven

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        environment: Literal["production", "staging"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async web-recruitment-sdk client instance.

        This automatically infers the `bearer_token` argument from the `BEARER_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("BEARER_TOKEN")
        if bearer_token is None:
            raise WebRecruitmentSDKError(
                "The bearer_token client option must be set either by passing bearer_token to the client or by setting the BEARER_TOKEN environment variable"
            )
        self.bearer_token = bearer_token

        self._environment = environment

        base_url_env = os.environ.get("WEB_RECRUITMENT_SDK_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `WEB_RECRUITMENT_SDK_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.auth = auth.AsyncAuthResource(self)
        self.admin = admin.AsyncAdminResource(self)
        self.patients = patients.AsyncPatientsResource(self)
        self.patients_by_external_id = patients_by_external_id.AsyncPatientsByExternalIDResource(self)
        self.protocols = protocols.AsyncProtocolsResource(self)
        self.protocol_parsings = protocol_parsings.AsyncProtocolParsingsResource(self)
        self.criteria = criteria.AsyncCriteriaResource(self)
        self.appointments = appointments.AsyncAppointmentsResource(self)
        self.sites = sites.AsyncSitesResource(self)
        self.health = health.AsyncHealthResource(self)
        self.system = system.AsyncSystemResource(self)
        self.feature_flags = feature_flags.AsyncFeatureFlagsResource(self)
        self.with_raw_response = AsyncWebRecruitmentSDKWithRawResponse(self)
        self.with_streaming_response = AsyncWebRecruitmentSDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        return {"Authorization": f"Bearer {bearer_token}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        environment: Literal["production", "staging"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    async def protocol_parsing(
        self,
        *,
        file: FileTypes,
        title: str,
        site_ids: Iterable[int] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ProtocolRead:
        """
        Upload Protocol

        Args:
          file: The protocol file to upload

          title: The title of the protocol

          site_ids: The site IDs to associate with the protocol

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self.post(
            "/protocol-parsing",
            body=await async_maybe_transform(
                {
                    "file": file,
                    "title": title,
                    "site_ids": site_ids,
                },
                client_protocol_parsing_params.ClientProtocolParsingParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProtocolRead,
        )

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class WebRecruitmentSDKWithRawResponse:
    def __init__(self, client: WebRecruitmentSDK) -> None:
        self.auth = auth.AuthResourceWithRawResponse(client.auth)
        self.admin = admin.AdminResourceWithRawResponse(client.admin)
        self.patients = patients.PatientsResourceWithRawResponse(client.patients)
        self.patients_by_external_id = patients_by_external_id.PatientsByExternalIDResourceWithRawResponse(
            client.patients_by_external_id
        )
        self.protocols = protocols.ProtocolsResourceWithRawResponse(client.protocols)
        self.protocol_parsings = protocol_parsings.ProtocolParsingsResourceWithRawResponse(client.protocol_parsings)
        self.criteria = criteria.CriteriaResourceWithRawResponse(client.criteria)
        self.appointments = appointments.AppointmentsResourceWithRawResponse(client.appointments)
        self.sites = sites.SitesResourceWithRawResponse(client.sites)
        self.health = health.HealthResourceWithRawResponse(client.health)
        self.system = system.SystemResourceWithRawResponse(client.system)
        self.feature_flags = feature_flags.FeatureFlagsResourceWithRawResponse(client.feature_flags)

        self.protocol_parsing = to_raw_response_wrapper(
            client.protocol_parsing,
        )


class AsyncWebRecruitmentSDKWithRawResponse:
    def __init__(self, client: AsyncWebRecruitmentSDK) -> None:
        self.auth = auth.AsyncAuthResourceWithRawResponse(client.auth)
        self.admin = admin.AsyncAdminResourceWithRawResponse(client.admin)
        self.patients = patients.AsyncPatientsResourceWithRawResponse(client.patients)
        self.patients_by_external_id = patients_by_external_id.AsyncPatientsByExternalIDResourceWithRawResponse(
            client.patients_by_external_id
        )
        self.protocols = protocols.AsyncProtocolsResourceWithRawResponse(client.protocols)
        self.protocol_parsings = protocol_parsings.AsyncProtocolParsingsResourceWithRawResponse(
            client.protocol_parsings
        )
        self.criteria = criteria.AsyncCriteriaResourceWithRawResponse(client.criteria)
        self.appointments = appointments.AsyncAppointmentsResourceWithRawResponse(client.appointments)
        self.sites = sites.AsyncSitesResourceWithRawResponse(client.sites)
        self.health = health.AsyncHealthResourceWithRawResponse(client.health)
        self.system = system.AsyncSystemResourceWithRawResponse(client.system)
        self.feature_flags = feature_flags.AsyncFeatureFlagsResourceWithRawResponse(client.feature_flags)

        self.protocol_parsing = async_to_raw_response_wrapper(
            client.protocol_parsing,
        )


class WebRecruitmentSDKWithStreamedResponse:
    def __init__(self, client: WebRecruitmentSDK) -> None:
        self.auth = auth.AuthResourceWithStreamingResponse(client.auth)
        self.admin = admin.AdminResourceWithStreamingResponse(client.admin)
        self.patients = patients.PatientsResourceWithStreamingResponse(client.patients)
        self.patients_by_external_id = patients_by_external_id.PatientsByExternalIDResourceWithStreamingResponse(
            client.patients_by_external_id
        )
        self.protocols = protocols.ProtocolsResourceWithStreamingResponse(client.protocols)
        self.protocol_parsings = protocol_parsings.ProtocolParsingsResourceWithStreamingResponse(
            client.protocol_parsings
        )
        self.criteria = criteria.CriteriaResourceWithStreamingResponse(client.criteria)
        self.appointments = appointments.AppointmentsResourceWithStreamingResponse(client.appointments)
        self.sites = sites.SitesResourceWithStreamingResponse(client.sites)
        self.health = health.HealthResourceWithStreamingResponse(client.health)
        self.system = system.SystemResourceWithStreamingResponse(client.system)
        self.feature_flags = feature_flags.FeatureFlagsResourceWithStreamingResponse(client.feature_flags)

        self.protocol_parsing = to_streamed_response_wrapper(
            client.protocol_parsing,
        )


class AsyncWebRecruitmentSDKWithStreamedResponse:
    def __init__(self, client: AsyncWebRecruitmentSDK) -> None:
        self.auth = auth.AsyncAuthResourceWithStreamingResponse(client.auth)
        self.admin = admin.AsyncAdminResourceWithStreamingResponse(client.admin)
        self.patients = patients.AsyncPatientsResourceWithStreamingResponse(client.patients)
        self.patients_by_external_id = patients_by_external_id.AsyncPatientsByExternalIDResourceWithStreamingResponse(
            client.patients_by_external_id
        )
        self.protocols = protocols.AsyncProtocolsResourceWithStreamingResponse(client.protocols)
        self.protocol_parsings = protocol_parsings.AsyncProtocolParsingsResourceWithStreamingResponse(
            client.protocol_parsings
        )
        self.criteria = criteria.AsyncCriteriaResourceWithStreamingResponse(client.criteria)
        self.appointments = appointments.AsyncAppointmentsResourceWithStreamingResponse(client.appointments)
        self.sites = sites.AsyncSitesResourceWithStreamingResponse(client.sites)
        self.health = health.AsyncHealthResourceWithStreamingResponse(client.health)
        self.system = system.AsyncSystemResourceWithStreamingResponse(client.system)
        self.feature_flags = feature_flags.AsyncFeatureFlagsResourceWithStreamingResponse(client.feature_flags)

        self.protocol_parsing = async_to_streamed_response_wrapper(
            client.protocol_parsing,
        )


Client = WebRecruitmentSDK

AsyncClient = AsyncWebRecruitmentSDK
