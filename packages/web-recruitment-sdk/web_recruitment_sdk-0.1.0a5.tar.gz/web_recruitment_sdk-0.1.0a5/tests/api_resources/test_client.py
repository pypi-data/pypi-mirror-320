# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.shared import ProtocolRead

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClient:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_protocol_parsing(self, client: WebRecruitmentSDK) -> None:
        client_ = client.protocol_parsing(
            file=b"raw file contents",
            title="title",
        )
        assert_matches_type(ProtocolRead, client_, path=["response"])

    @parametrize
    def test_method_protocol_parsing_with_all_params(self, client: WebRecruitmentSDK) -> None:
        client_ = client.protocol_parsing(
            file=b"raw file contents",
            title="title",
            site_ids=[0],
        )
        assert_matches_type(ProtocolRead, client_, path=["response"])

    @parametrize
    def test_raw_response_protocol_parsing(self, client: WebRecruitmentSDK) -> None:
        response = client.with_raw_response.protocol_parsing(
            file=b"raw file contents",
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(ProtocolRead, client_, path=["response"])

    @parametrize
    def test_streaming_response_protocol_parsing(self, client: WebRecruitmentSDK) -> None:
        with client.with_streaming_response.protocol_parsing(
            file=b"raw file contents",
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(ProtocolRead, client_, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClient:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_protocol_parsing(self, async_client: AsyncWebRecruitmentSDK) -> None:
        client = await async_client.protocol_parsing(
            file=b"raw file contents",
            title="title",
        )
        assert_matches_type(ProtocolRead, client, path=["response"])

    @parametrize
    async def test_method_protocol_parsing_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        client = await async_client.protocol_parsing(
            file=b"raw file contents",
            title="title",
            site_ids=[0],
        )
        assert_matches_type(ProtocolRead, client, path=["response"])

    @parametrize
    async def test_raw_response_protocol_parsing(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.with_raw_response.protocol_parsing(
            file=b"raw file contents",
            title="title",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(ProtocolRead, client, path=["response"])

    @parametrize
    async def test_streaming_response_protocol_parsing(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.with_streaming_response.protocol_parsing(
            file=b"raw file contents",
            title="title",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(ProtocolRead, client, path=["response"])

        assert cast(Any, response.is_closed) is True
