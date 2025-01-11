# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk.types.shared import SiteRead
from web_recruitment_sdk.types.system import SiteListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSites:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        site = client.system.sites.create(
            tenant_id="tenant_id",
            name="name",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: WebRecruitmentSDK) -> None:
        site = client.system.sites.create(
            tenant_id="tenant_id",
            name="name",
            trially_site_id="triallySiteId",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.system.sites.with_raw_response.create(
            tenant_id="tenant_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = response.parse()
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.system.sites.with_streaming_response.create(
            tenant_id="tenant_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = response.parse()
            assert_matches_type(SiteRead, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.sites.with_raw_response.create(
                tenant_id="",
                name="name",
            )

    @parametrize
    def test_method_retrieve(self, client: WebRecruitmentSDK) -> None:
        site = client.system.sites.retrieve(
            site_id="site_id",
            tenant_id="tenant_id",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        response = client.system.sites.with_raw_response.retrieve(
            site_id="site_id",
            tenant_id="tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = response.parse()
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: WebRecruitmentSDK) -> None:
        with client.system.sites.with_streaming_response.retrieve(
            site_id="site_id",
            tenant_id="tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = response.parse()
            assert_matches_type(SiteRead, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.sites.with_raw_response.retrieve(
                site_id="site_id",
                tenant_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `site_id` but received ''"):
            client.system.sites.with_raw_response.retrieve(
                site_id="",
                tenant_id="tenant_id",
            )

    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        site = client.system.sites.update(
            site_id="site_id",
            tenant_id="tenant_id",
            name="name",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: WebRecruitmentSDK) -> None:
        site = client.system.sites.update(
            site_id="site_id",
            tenant_id="tenant_id",
            name="name",
            trially_site_id="triallySiteId",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.system.sites.with_raw_response.update(
            site_id="site_id",
            tenant_id="tenant_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = response.parse()
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.system.sites.with_streaming_response.update(
            site_id="site_id",
            tenant_id="tenant_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = response.parse()
            assert_matches_type(SiteRead, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.sites.with_raw_response.update(
                site_id="site_id",
                tenant_id="",
                name="name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `site_id` but received ''"):
            client.system.sites.with_raw_response.update(
                site_id="",
                tenant_id="tenant_id",
                name="name",
            )

    @parametrize
    def test_method_list(self, client: WebRecruitmentSDK) -> None:
        site = client.system.sites.list(
            "tenant_id",
        )
        assert_matches_type(SiteListResponse, site, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: WebRecruitmentSDK) -> None:
        response = client.system.sites.with_raw_response.list(
            "tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = response.parse()
        assert_matches_type(SiteListResponse, site, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: WebRecruitmentSDK) -> None:
        with client.system.sites.with_streaming_response.list(
            "tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = response.parse()
            assert_matches_type(SiteListResponse, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.sites.with_raw_response.list(
                "",
            )

    @parametrize
    def test_method_delete(self, client: WebRecruitmentSDK) -> None:
        site = client.system.sites.delete(
            site_id="site_id",
            tenant_id="tenant_id",
        )
        assert_matches_type(object, site, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: WebRecruitmentSDK) -> None:
        response = client.system.sites.with_raw_response.delete(
            site_id="site_id",
            tenant_id="tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = response.parse()
        assert_matches_type(object, site, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: WebRecruitmentSDK) -> None:
        with client.system.sites.with_streaming_response.delete(
            site_id="site_id",
            tenant_id="tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = response.parse()
            assert_matches_type(object, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.sites.with_raw_response.delete(
                site_id="site_id",
                tenant_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `site_id` but received ''"):
            client.system.sites.with_raw_response.delete(
                site_id="",
                tenant_id="tenant_id",
            )


class TestAsyncSites:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.system.sites.create(
            tenant_id="tenant_id",
            name="name",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.system.sites.create(
            tenant_id="tenant_id",
            name="name",
            trially_site_id="triallySiteId",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.sites.with_raw_response.create(
            tenant_id="tenant_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = await response.parse()
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.sites.with_streaming_response.create(
            tenant_id="tenant_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = await response.parse()
            assert_matches_type(SiteRead, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.sites.with_raw_response.create(
                tenant_id="",
                name="name",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.system.sites.retrieve(
            site_id="site_id",
            tenant_id="tenant_id",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.sites.with_raw_response.retrieve(
            site_id="site_id",
            tenant_id="tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = await response.parse()
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.sites.with_streaming_response.retrieve(
            site_id="site_id",
            tenant_id="tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = await response.parse()
            assert_matches_type(SiteRead, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.sites.with_raw_response.retrieve(
                site_id="site_id",
                tenant_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `site_id` but received ''"):
            await async_client.system.sites.with_raw_response.retrieve(
                site_id="",
                tenant_id="tenant_id",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.system.sites.update(
            site_id="site_id",
            tenant_id="tenant_id",
            name="name",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.system.sites.update(
            site_id="site_id",
            tenant_id="tenant_id",
            name="name",
            trially_site_id="triallySiteId",
        )
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.sites.with_raw_response.update(
            site_id="site_id",
            tenant_id="tenant_id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = await response.parse()
        assert_matches_type(SiteRead, site, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.sites.with_streaming_response.update(
            site_id="site_id",
            tenant_id="tenant_id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = await response.parse()
            assert_matches_type(SiteRead, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.sites.with_raw_response.update(
                site_id="site_id",
                tenant_id="",
                name="name",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `site_id` but received ''"):
            await async_client.system.sites.with_raw_response.update(
                site_id="",
                tenant_id="tenant_id",
                name="name",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.system.sites.list(
            "tenant_id",
        )
        assert_matches_type(SiteListResponse, site, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.sites.with_raw_response.list(
            "tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = await response.parse()
        assert_matches_type(SiteListResponse, site, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.sites.with_streaming_response.list(
            "tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = await response.parse()
            assert_matches_type(SiteListResponse, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.sites.with_raw_response.list(
                "",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        site = await async_client.system.sites.delete(
            site_id="site_id",
            tenant_id="tenant_id",
        )
        assert_matches_type(object, site, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.sites.with_raw_response.delete(
            site_id="site_id",
            tenant_id="tenant_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        site = await response.parse()
        assert_matches_type(object, site, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.sites.with_streaming_response.delete(
            site_id="site_id",
            tenant_id="tenant_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            site = await response.parse()
            assert_matches_type(object, site, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.sites.with_raw_response.delete(
                site_id="site_id",
                tenant_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `site_id` but received ''"):
            await async_client.system.sites.with_raw_response.delete(
                site_id="",
                tenant_id="tenant_id",
            )
