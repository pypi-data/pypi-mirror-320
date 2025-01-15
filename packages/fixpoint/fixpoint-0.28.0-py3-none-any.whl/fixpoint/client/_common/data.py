"""Common interface for interacting with datasets (pre-built and custom)"""

__all__ = [
    "match_person",
    "async_match_person",
    "get_company",
    "async_get_company",
    "create_patent_extraction",
    "async_create_patent_extraction",
]

import httpx

from fixpoint_common.types.people import PersonData
from fixpoint_common.types.companies import CompanyData
from fixpoint_common.types.patent_extraction import (
    CreatePatentExtractionRequest,
    CreatePatentExtractionResponse,
)
from fixpoint.errors import raise_for_status
from .core import ApiCoreConfig, RequestOptions

_PERSON_ROUTE = "/people"
_COMPANY_ROUTE = "/companies"
_PATENT_EXTRACT_ROUTE = "/extractions/patent_extractions"


def match_person(
    http_client: httpx.Client,
    config: ApiCoreConfig,
    opts: RequestOptions,
    *,
    linkedin_url: str,
) -> PersonData:
    """Match an identifier to a person and their data."""
    resp = http_client.get(
        config.route_url(f"{_PERSON_ROUTE}:match"),
        params={"linkedin_url": linkedin_url},
        timeout=opts.get("timeout_s", httpx.USE_CLIENT_DEFAULT),
    )
    return _process_person_match_response(resp)


async def async_match_person(
    http_client: httpx.AsyncClient,
    config: ApiCoreConfig,
    opts: RequestOptions,
    *,
    linkedin_url: str,
) -> PersonData:
    """Async match an identifier to a person and their data."""
    resp = await http_client.get(
        config.route_url(f"{_PERSON_ROUTE}:match"),
        params={"linkedin_url": linkedin_url},
        timeout=opts.get("timeout_s", httpx.USE_CLIENT_DEFAULT),
    )
    return _process_person_match_response(resp)


def _process_person_match_response(resp: httpx.Response) -> PersonData:
    raise_for_status(resp)
    return PersonData.model_validate(resp.json())


def get_company(
    http_client: httpx.Client,
    config: ApiCoreConfig,
    opts: RequestOptions,
    *,
    company_id: str,
) -> CompanyData:
    """Get company data by ID."""
    resp = http_client.get(
        config.route_url(_COMPANY_ROUTE, company_id),
        timeout=opts.get("timeout_s", httpx.USE_CLIENT_DEFAULT),
    )
    return _process_company_response(resp)


async def async_get_company(
    http_client: httpx.AsyncClient,
    config: ApiCoreConfig,
    opts: RequestOptions,
    *,
    company_id: str,
) -> CompanyData:
    """Get company data by ID asynchronously."""
    resp = await http_client.get(
        config.route_url(_COMPANY_ROUTE, company_id),
        timeout=opts.get("timeout_s", httpx.USE_CLIENT_DEFAULT),
    )
    return _process_company_response(resp)


def _process_company_response(resp: httpx.Response) -> CompanyData:
    raise_for_status(resp)
    return CompanyData.model_validate(resp.json())


def create_patent_extraction(
    http_client: httpx.Client,
    config: ApiCoreConfig,
    opts: RequestOptions,
    *,
    request: CreatePatentExtractionRequest,
) -> CreatePatentExtractionResponse:
    """Create a patent extraction."""
    resp = http_client.post(
        config.route_url(_PATENT_EXTRACT_ROUTE),
        json=request.model_dump(),
        timeout=opts.get("timeout_s", httpx.USE_CLIENT_DEFAULT),
    )
    return _process_patent_extraction_response(resp)


async def async_create_patent_extraction(
    http_client: httpx.AsyncClient,
    config: ApiCoreConfig,
    opts: RequestOptions,
    *,
    request: CreatePatentExtractionRequest,
) -> CreatePatentExtractionResponse:
    """Async create a patent extraction."""
    resp = await http_client.post(
        config.route_url(_PATENT_EXTRACT_ROUTE),
        json=request.model_dump(),
        timeout=opts.get("timeout_s", httpx.USE_CLIENT_DEFAULT),
    )
    return _process_patent_extraction_response(resp)


def _process_patent_extraction_response(
    resp: httpx.Response,
) -> CreatePatentExtractionResponse:
    raise_for_status(resp)
    return CreatePatentExtractionResponse.model_validate(resp.json())
