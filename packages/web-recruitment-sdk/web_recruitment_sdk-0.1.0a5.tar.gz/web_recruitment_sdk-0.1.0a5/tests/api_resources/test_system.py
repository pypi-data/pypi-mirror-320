# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSystem:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_ping(self, client: WebRecruitmentSDK) -> None:
        system = client.system.ping()
        assert_matches_type(object, system, path=["response"])

    @parametrize
    def test_raw_response_ping(self, client: WebRecruitmentSDK) -> None:
        response = client.system.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = response.parse()
        assert_matches_type(object, system, path=["response"])

    @parametrize
    def test_streaming_response_ping(self, client: WebRecruitmentSDK) -> None:
        with client.system.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = response.parse()
            assert_matches_type(object, system, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSystem:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_ping(self, async_client: AsyncWebRecruitmentSDK) -> None:
        system = await async_client.system.ping()
        assert_matches_type(object, system, path=["response"])

    @parametrize
    async def test_raw_response_ping(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.with_raw_response.ping()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        system = await response.parse()
        assert_matches_type(object, system, path=["response"])

    @parametrize
    async def test_streaming_response_ping(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.with_streaming_response.ping() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            system = await response.parse()
            assert_matches_type(object, system, path=["response"])

        assert cast(Any, response.is_closed) is True
