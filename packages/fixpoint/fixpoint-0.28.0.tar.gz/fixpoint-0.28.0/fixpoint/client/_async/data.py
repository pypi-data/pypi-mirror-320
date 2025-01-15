"""Async client for interacting with datasets (pre-built and custom)"""

__all__ = ["AsyncData"]

from typing import Optional

from fixpoint_common.types.people import PersonData
from fixpoint_common.types.companies import CompanyData
from fixpoint_common.types.patent_extraction import (
    CreatePatentExtractionRequest,
    CreatePatentExtractionResponse,
)
from .._common.core import RequestOptions
from .._common.data import (
    async_match_person,
    async_get_company,
    async_create_patent_extraction,
)
from ._config import AsyncConfig


class _AsyncPeople:
    _config: AsyncConfig

    def __init__(self, config: AsyncConfig):
        self._config = config

    async def match(
        self, *, linkedin_url: str, opts: Optional[RequestOptions] = None
    ) -> PersonData:
        """Match an identifier to a person and their data.

        Args:
            linkedin_url (str): The LinkedIn URL to match.

        Returns:
            PersonData: The person data.

        Raises:
            FixpointApiError: If there's an error in the HTTP request.
        """
        return await async_match_person(
            self._config.http_client,
            self._config.core,
            opts or {},
            linkedin_url=linkedin_url,
        )


class _AsyncCompanies:
    _config: AsyncConfig

    def __init__(self, config: AsyncConfig):
        self._config = config

    async def get(
        self, *, company_id: str, opts: Optional[RequestOptions] = None
    ) -> CompanyData:
        """Get company data by ID.

        Args:
            company_id (str): The ID of the company to retrieve.

        Returns:
            CompanyData: The company data.

        Raises:
            FixpointApiError: If there's an error in the HTTP request.
        """
        return await async_get_company(
            self._config.http_client,
            self._config.core,
            opts or {},
            company_id=company_id,
        )


class _AsyncPatents:
    _config: AsyncConfig

    def __init__(self, config: AsyncConfig):
        self._config = config

    async def create_extraction(
        self,
        request: CreatePatentExtractionRequest,
        opts: Optional[RequestOptions] = None,
    ) -> CreatePatentExtractionResponse:
        """Create a patent extraction request.

        Args:
            request (CreatePatentExtractionRequest): The patent extraction request.

        Returns:
            CreatePatentExtractionResponse: The patent extraction response.

        Raises:
            FixpointApiError: If there's an error in the HTTP request.
        """
        return await async_create_patent_extraction(
            self._config.http_client,
            self._config.core,
            opts or {},
            request=request,
        )


class AsyncData:
    """Async client for interacting with datasets (pre-built and custom)"""

    _config: AsyncConfig
    _people: _AsyncPeople
    _companies: _AsyncCompanies
    _patents: _AsyncPatents

    def __init__(self, config: AsyncConfig):
        self._config = config
        self._people = _AsyncPeople(config)
        self._companies = _AsyncCompanies(config)
        self._patents = _AsyncPatents(config)

    @property
    def people(self) -> _AsyncPeople:
        """Interface for people data"""
        return self._people

    @property
    def companies(self) -> _AsyncCompanies:
        """Interface for companies data"""
        return self._companies

    @property
    def patents(self) -> _AsyncPatents:
        """Interface for patents data"""
        return self._patents
