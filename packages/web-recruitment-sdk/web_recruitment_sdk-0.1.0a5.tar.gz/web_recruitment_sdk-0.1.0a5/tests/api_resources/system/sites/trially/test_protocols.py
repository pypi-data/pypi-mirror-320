# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.system.sites.trially import ProtocolListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProtocols:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        protocol = client.system.sites.trially.protocols.list(
            trially_site_id="trially_site_id",
            tenant_id="tenant_id",
        )
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.system.sites.trially.protocols.with_raw_response.list(
            trially_site_id="trially_site_id",
            tenant_id="tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = response.parse()
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.system.sites.trially.protocols.with_streaming_response.list(
            trially_site_id="trially_site_id",
            tenant_id="tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = response.parse()
            assert_matches_type(ProtocolListResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.sites.trially.protocols.with_raw_response.list(
                trially_site_id="trially_site_id",
                tenant_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `trially_site_id` but received ''"):
            client.system.sites.trially.protocols.with_raw_response.list(
                trially_site_id="",
                tenant_id="tenant_id",
            )


class TestAsyncProtocols:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        protocol = await async_client.system.sites.trially.protocols.list(
            trially_site_id="trially_site_id",
            tenant_id="tenant_id",
        )
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.sites.trially.protocols.with_raw_response.list(
            trially_site_id="trially_site_id",
            tenant_id="tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        protocol = await response.parse()
        assert_matches_type(ProtocolListResponse, protocol, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.sites.trially.protocols.with_streaming_response.list(
            trially_site_id="trially_site_id",
            tenant_id="tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            protocol = await response.parse()
            assert_matches_type(ProtocolListResponse, protocol, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.sites.trially.protocols.with_raw_response.list(
                trially_site_id="trially_site_id",
                tenant_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `trially_site_id` but received ''"):
            await async_client.system.sites.trially.protocols.with_raw_response.list(
                trially_site_id="",
                tenant_id="tenant_id",
            )
