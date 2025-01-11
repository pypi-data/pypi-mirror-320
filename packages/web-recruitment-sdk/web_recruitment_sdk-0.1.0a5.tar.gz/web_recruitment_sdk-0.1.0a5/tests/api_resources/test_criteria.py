# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.shared import CriteriaRead

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCriteria:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        criterion = client.criteria.create(
            protocol_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: WebRecruitmentSDK) -> None:
        criterion = client.criteria.create(
            protocol_id=0,
            summary="summary",
            type="inclusion",
            description="description",
            status="active",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.criteria.with_raw_response.create(
            protocol_id=0,
            summary="summary",
            type="inclusion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.criteria.with_streaming_response.create(
            protocol_id=0,
            summary="summary",
            type="inclusion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        criterion = client.criteria.retrieve(
            0,
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.criteria.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.criteria.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        criterion = client.criteria.update(
            criterion_id=0,
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: WebRecruitmentSDK) -> None:
        criterion = client.criteria.update(
            criterion_id=0,
            description="description",
            status="active",
            summary="summary",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.criteria.with_raw_response.update(
            criterion_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.criteria.with_streaming_response.update(
            criterion_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCriteria:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.criteria.create(
            protocol_id=0,
            summary="summary",
            type="inclusion",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.criteria.create(
            protocol_id=0,
            summary="summary",
            type="inclusion",
            description="description",
            status="active",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.criteria.with_raw_response.create(
            protocol_id=0,
            summary="summary",
            type="inclusion",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.criteria.with_streaming_response.create(
            protocol_id=0,
            summary="summary",
            type="inclusion",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.criteria.retrieve(
            0,
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.criteria.with_raw_response.retrieve(
            0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.criteria.with_streaming_response.retrieve(
            0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.criteria.update(
            criterion_id=0,
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criterion = await async_client.criteria.update(
            criterion_id=0,
            description="description",
            status="active",
            summary="summary",
        )
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.criteria.with_raw_response.update(
            criterion_id=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criterion = await response.parse()
        assert_matches_type(CriteriaRead, criterion, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.criteria.with_streaming_response.update(
            criterion_id=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criterion = await response.parse()
            assert_matches_type(CriteriaRead, criterion, path=["response"])

        assert cast(Any, response.is_closed) is True
