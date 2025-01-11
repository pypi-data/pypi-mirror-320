# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from web_recruitment_sdk import WebRecruitmentSDK, AsyncWebRecruitmentSDK
from web_recruitment_sdk._utils import parse_date
from web_recruitment_sdk.types.shared import PatientRead
from web_recruitment_sdk.types.system import (
    BulkInsertResult,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPatients:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.create(
            tenant_id="tenant_id",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.create(
            tenant_id="tenant_id",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
            do_not_call=True,
            middle_name="middleName",
            phone="phone",
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.with_raw_response.create(
            tenant_id="tenant_id",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.with_streaming_response.create(
            tenant_id="tenant_id",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.patients.with_raw_response.create(
                tenant_id="",
                dob=parse_date("2019-12-27"),
                email="email",
                family_name="familyName",
                given_name="givenName",
                site_id=0,
                trially_patient_id="triallyPatientId",
            )

    @parametrize
    def test_method_update(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.update(
            patient_id=0,
            tenant_id="tenant_id",
            do_not_call=True,
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.with_raw_response.update(
            patient_id=0,
            tenant_id="tenant_id",
            do_not_call=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.with_streaming_response.update(
            patient_id=0,
            tenant_id="tenant_id",
            do_not_call=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.patients.with_raw_response.update(
                patient_id=0,
                tenant_id="",
                do_not_call=True,
            )

    @parametrize
    def test_method_bulk_allergies(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.bulk_allergies(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_raw_response_bulk_allergies(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.with_raw_response.bulk_allergies(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_streaming_response_bulk_allergies(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.with_streaming_response.bulk_allergies(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_bulk_allergies(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.patients.with_raw_response.bulk_allergies(
                tenant_id="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_allergy_id": "triallyAllergyId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @parametrize
    def test_method_bulk_conditions(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.bulk_conditions(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_raw_response_bulk_conditions(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.with_raw_response.bulk_conditions(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_streaming_response_bulk_conditions(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.with_streaming_response.bulk_conditions(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_bulk_conditions(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.patients.with_raw_response.bulk_conditions(
                tenant_id="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_condition_id": "triallyConditionId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @parametrize
    def test_method_bulk_medications(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.bulk_medications(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_raw_response_bulk_medications(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.with_raw_response.bulk_medications(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_streaming_response_bulk_medications(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.with_streaming_response.bulk_medications(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_bulk_medications(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.patients.with_raw_response.bulk_medications(
                tenant_id="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_medication_id": "triallyMedicationId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @parametrize
    def test_method_bulk_procedures(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.bulk_procedures(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_raw_response_bulk_procedures(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.with_raw_response.bulk_procedures(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_streaming_response_bulk_procedures(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.with_streaming_response.bulk_procedures(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_bulk_procedures(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.patients.with_raw_response.bulk_procedures(
                tenant_id="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_patient_id": "triallyPatientId",
                        "trially_procedure_id": "triallyProcedureId",
                    }
                ],
            )

    @parametrize
    def test_method_bulk_update(self, client: WebRecruitmentSDK) -> None:
        patient = client.system.patients.bulk_update(
            tenant_id="tenant_id",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_raw_response_bulk_update(self, client: WebRecruitmentSDK) -> None:
        response = client.system.patients.with_raw_response.bulk_update(
            tenant_id="tenant_id",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    def test_streaming_response_bulk_update(self, client: WebRecruitmentSDK) -> None:
        with client.system.patients.with_streaming_response.bulk_update(
            tenant_id="tenant_id",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_bulk_update(self, client: WebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            client.system.patients.with_raw_response.bulk_update(
                tenant_id="",
                body=[
                    {
                        "dob": parse_date("2019-12-27"),
                        "email": "email",
                        "family_name": "familyName",
                        "given_name": "givenName",
                        "site_id": 0,
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )


class TestAsyncPatients:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.create(
            tenant_id="tenant_id",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.create(
            tenant_id="tenant_id",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
            do_not_call=True,
            middle_name="middleName",
            phone="phone",
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.with_raw_response.create(
            tenant_id="tenant_id",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.with_streaming_response.create(
            tenant_id="tenant_id",
            dob=parse_date("2019-12-27"),
            email="email",
            family_name="familyName",
            given_name="givenName",
            site_id=0,
            trially_patient_id="triallyPatientId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.patients.with_raw_response.create(
                tenant_id="",
                dob=parse_date("2019-12-27"),
                email="email",
                family_name="familyName",
                given_name="givenName",
                site_id=0,
                trially_patient_id="triallyPatientId",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.update(
            patient_id=0,
            tenant_id="tenant_id",
            do_not_call=True,
        )
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.with_raw_response.update(
            patient_id=0,
            tenant_id="tenant_id",
            do_not_call=True,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(PatientRead, patient, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.with_streaming_response.update(
            patient_id=0,
            tenant_id="tenant_id",
            do_not_call=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(PatientRead, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.patients.with_raw_response.update(
                patient_id=0,
                tenant_id="",
                do_not_call=True,
            )

    @parametrize
    async def test_method_bulk_allergies(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.bulk_allergies(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_raw_response_bulk_allergies(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.with_raw_response.bulk_allergies(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_streaming_response_bulk_allergies(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.with_streaming_response.bulk_allergies(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_allergy_id": "triallyAllergyId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_bulk_allergies(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.patients.with_raw_response.bulk_allergies(
                tenant_id="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_allergy_id": "triallyAllergyId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @parametrize
    async def test_method_bulk_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.bulk_conditions(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_raw_response_bulk_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.with_raw_response.bulk_conditions(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_streaming_response_bulk_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.with_streaming_response.bulk_conditions(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_condition_id": "triallyConditionId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_bulk_conditions(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.patients.with_raw_response.bulk_conditions(
                tenant_id="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_condition_id": "triallyConditionId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @parametrize
    async def test_method_bulk_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.bulk_medications(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_raw_response_bulk_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.with_raw_response.bulk_medications(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_streaming_response_bulk_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.with_streaming_response.bulk_medications(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_medication_id": "triallyMedicationId",
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_bulk_medications(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.patients.with_raw_response.bulk_medications(
                tenant_id="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_medication_id": "triallyMedicationId",
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )

    @parametrize
    async def test_method_bulk_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.bulk_procedures(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_raw_response_bulk_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.with_raw_response.bulk_procedures(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_streaming_response_bulk_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.with_streaming_response.bulk_procedures(
            tenant_id="tenant_id",
            body=[
                {
                    "cui": "cui",
                    "name": "name",
                    "trially_patient_id": "triallyPatientId",
                    "trially_procedure_id": "triallyProcedureId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_bulk_procedures(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.patients.with_raw_response.bulk_procedures(
                tenant_id="",
                body=[
                    {
                        "cui": "cui",
                        "name": "name",
                        "trially_patient_id": "triallyPatientId",
                        "trially_procedure_id": "triallyProcedureId",
                    }
                ],
            )

    @parametrize
    async def test_method_bulk_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        patient = await async_client.system.patients.bulk_update(
            tenant_id="tenant_id",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_raw_response_bulk_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        response = await async_client.system.patients.with_raw_response.bulk_update(
            tenant_id="tenant_id",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        patient = await response.parse()
        assert_matches_type(BulkInsertResult, patient, path=["response"])

    @parametrize
    async def test_streaming_response_bulk_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        async with async_client.system.patients.with_streaming_response.bulk_update(
            tenant_id="tenant_id",
            body=[
                {
                    "dob": parse_date("2019-12-27"),
                    "email": "email",
                    "family_name": "familyName",
                    "given_name": "givenName",
                    "site_id": 0,
                    "trially_patient_id": "triallyPatientId",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            patient = await response.parse()
            assert_matches_type(BulkInsertResult, patient, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_bulk_update(self, async_client: AsyncWebRecruitmentSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `tenant_id` but received ''"):
            await async_client.system.patients.with_raw_response.bulk_update(
                tenant_id="",
                body=[
                    {
                        "dob": parse_date("2019-12-27"),
                        "email": "email",
                        "family_name": "familyName",
                        "given_name": "givenName",
                        "site_id": 0,
                        "trially_patient_id": "triallyPatientId",
                    }
                ],
            )
