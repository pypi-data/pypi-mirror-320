"""Client for interacting with datasets (pre-built and custom)"""

__all__ = ["Data"]

from typing import Optional

from fixpoint_common.types.people import PersonData
from fixpoint_common.types.companies import CompanyData
from fixpoint_common.types.patent_extraction import (
    CreatePatentExtractionRequest,
    CreatePatentExtractionResponse,
)
from .._common.data import (
    match_person,
    get_company,
    create_patent_extraction,
)
from .._common.core import RequestOptions
from ._config import Config


class _People:
    _config: Config

    def __init__(self, config: Config):
        self._config = config

    def match(
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
        return match_person(
            self._config.http_client,
            self._config.core,
            opts or {},
            linkedin_url=linkedin_url,
        )


class _Companies:
    _config: Config

    def __init__(self, config: Config):
        self._config = config

    def get(
        self, *, company_id: str, opts: Optional[RequestOptions] = None
    ) -> CompanyData:
        """Get company data by ID.

        Args:
            company_id (str): The ID of the company to retrieve.
            opts (Optional[RequestOptions]): Request options.

        Returns:
            CompanyData: The company data.

        Raises:
            FixpointApiError: If there's an error in the HTTP request.
        """
        return get_company(
            self._config.http_client,
            self._config.core,
            opts or {},
            company_id=company_id,
        )


class _Patents:
    _config: Config

    def __init__(self, config: Config):
        self._config = config

    def create_extraction(
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
        return create_patent_extraction(
            self._config.http_client,
            self._config.core,
            opts or {},
            request=request,
        )


class Data:
    """Sync client for interacting with datasets (pre-built and custom)"""

    _config: Config
    _people: _People
    _companies: _Companies
    _patents: _Patents

    def __init__(self, config: Config):
        self._config = config
        self._people = _People(config)
        self._companies = _Companies(config)
        self._patents = _Patents(config)

    @property
    def people(self) -> _People:
        """Interface for people data"""
        return self._people

    @property
    def companies(self) -> _Companies:
        """Interface for companies data"""
        return self._companies

    @property
    def patents(self) -> _Patents:
        """Interface for patents data"""
        return self._patents
