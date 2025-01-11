# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.protocols import CriteriaInstanceListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCriteriaInstances:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        criteria_instance = client.protocols.criteria_instances.list(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        )
        assert_matches_type(CriteriaInstanceListResponse, criteria_instance, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.protocols.criteria_instances.with_raw_response.list(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criteria_instance = response.parse()
        assert_matches_type(CriteriaInstanceListResponse, criteria_instance, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.protocols.criteria_instances.with_streaming_response.list(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criteria_instance = response.parse()
            assert_matches_type(CriteriaInstanceListResponse, criteria_instance, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCriteriaInstances:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        criteria_instance = await async_client.protocols.criteria_instances.list(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        )
        assert_matches_type(CriteriaInstanceListResponse, criteria_instance, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.protocols.criteria_instances.with_raw_response.list(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        criteria_instance = await response.parse()
        assert_matches_type(CriteriaInstanceListResponse, criteria_instance, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.protocols.criteria_instances.with_streaming_response.list(
            protocol_id=0,
            trially_patient_id="trially_patient_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            criteria_instance = await response.parse()
            assert_matches_type(CriteriaInstanceListResponse, criteria_instance, path=["response"])

        assert cast(Any, response.is_closed) is True
