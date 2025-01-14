import os
from datetime import datetime
from typing import Any, Optional, Union, cast
import ssl

import aiohttp
from pydantic import BaseModel

from .logger import logger
from .models import (
    Filing, Company, Sector, IndustryGroup, Industry, SubIndustry,
    FilingResponse, CompanyResponse, FilingTypeResponse, SourceResponse,
    SectorResponse, IndustryResponse
)


class FinancialReportsRequest(BaseModel):
    """Base model for Financial Reports API requests."""
    page: int = 1
    page_size: int = 50


class FilingsRequest(FinancialReportsRequest):
    """Model for filings list request parameters."""
    company_isin: Optional[str] = None
    lei: Optional[str] = None
    countries: Optional[str] = None
    language: Optional[str] = None
    added_to_platform_from: Optional[Union[str, datetime]] = None
    added_to_platform_to: Optional[Union[str, datetime]] = None
    dissemination_datetime_from: Optional[Union[str, datetime]] = None
    dissemination_datetime_to: Optional[Union[str, datetime]] = None
    release_datetime_from: Optional[Union[str, datetime]] = None
    release_datetime_to: Optional[Union[str, datetime]] = None
    type: Optional[str] = None
    search: Optional[str] = None
    ordering: Optional[str] = None


class CompaniesRequest(FinancialReportsRequest):
    """Model for companies list request parameters."""
    countries: Optional[str] = None
    sector: Optional[int] = None
    industry_group: Optional[int] = None
    industry: Optional[int] = None
    sub_industry: Optional[int] = None

class FinancialReportsClient:
    """Async client for interacting with the Financial Reports API."""

    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "https://api.financialreports.eu",
        verify_ssl: bool = True
    ):
        """Initialize the Financial Reports API client."""
        self.api_key = api_key or os.getenv("FINANCIAL_REPORTS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either directly or via FINANCIAL_REPORTS_API_KEY environment variable"
            )
        self.base_url = base_url.rstrip("/")
        self.verify_ssl = verify_ssl
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers={"x-api-key": self.api_key}  # Remove ssl parameter from here
            )
        return self._session

    async def close(self):
        """Close the client session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _make_request(
        self, method: str, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a request to the API."""
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()

        # Create SSL context if verification is disabled
        ssl_context = None
        if not self.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            logger.warning("SSL verification is disabled")

        try:
            # Pass ssl_context to the request
            async with session.request(method, url, params=params, ssl=ssl_context) as response:
                if response.status != 200:
                    error_data = await response.json()
                    logger.error(f"Financial Reports API error: {error_data}")
                    if response.status == 401:
                        raise ValueError("Invalid API key")
                    elif response.status == 403:
                        raise ValueError("Insufficient permissions")
                    response.raise_for_status()

                data = await response.json()
                if not isinstance(data, dict):
                    raise ValueError(f"Expected dict response, got {type(data)}")
                return data
        except Exception as e:
            logger.error(f"Error making request to Financial Reports API: {str(e)}")
            raise

    async def list_filings(
        self,
        page: int = 1,
        page_size: int = 50,
        company_isin: Optional[str] = None,
        lei: Optional[str] = None,
        countries: Optional[str] = None,
        language: Optional[str] = None,
        added_to_platform_from: Optional[Union[str, datetime]] = None,
        added_to_platform_to: Optional[Union[str, datetime]] = None,
        dissemination_datetime_from: Optional[Union[str, datetime]] = None,
        dissemination_datetime_to: Optional[Union[str, datetime]] = None,
        release_datetime_from: Optional[Union[str, datetime]] = None,
        release_datetime_to: Optional[Union[str, datetime]] = None,
        type: Optional[str] = None,
        search: Optional[str] = None,
        ordering: Optional[str] = None,
    ) -> FilingResponse:
        """
        List financial filings with optional filtering.

        Args:
            page: Page number for pagination
            page_size: Number of results per page
            company_isin: Filter by company ISIN
            lei: Filter by company LEI
            countries: Filter by ISO 3166-1 alpha-2 country code
            language: Filter by ISO 639-1 language code
            added_to_platform_from: Filter by minimum date added to platform (ISO 8601)
            added_to_platform_to: Filter by maximum date added to platform (ISO 8601)
            dissemination_datetime_from: Filter by minimum dissemination date (ISO 8601)
            dissemination_datetime_to: Filter by maximum dissemination date (ISO 8601)
            release_datetime_from: Filter by minimum release date (ISO 8601)
            release_datetime_to: Filter by maximum release date (ISO 8601)
            type: Filter by filing type code
            search: Text search query
            ordering: Field to order by (prefix with - for descending)

        Returns:
            Dict containing:
                count: Total number of results
                next: URL for next page
                previous: URL for previous page
                results: List of filing objects
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}

        # Add optional filters
        if company_isin:
            params["company_isin"] = company_isin
        if lei:
            params["lei"] = lei
        if countries:
            params["countries"] = countries
        if language:
            params["language"] = language
        if added_to_platform_from:
            params["added_to_platform_from"] = (
                added_to_platform_from.isoformat()
                if isinstance(added_to_platform_from, datetime)
                else added_to_platform_from
            )
        if added_to_platform_to:
            params["added_to_platform_to"] = (
                added_to_platform_to.isoformat()
                if isinstance(added_to_platform_to, datetime)
                else added_to_platform_to
            )
        if dissemination_datetime_from:
            params["dissemination_datetime_from"] = (
                dissemination_datetime_from.isoformat()
                if isinstance(dissemination_datetime_from, datetime)
                else dissemination_datetime_from
            )
        if dissemination_datetime_to:
            params["dissemination_datetime_to"] = (
                dissemination_datetime_to.isoformat()
                if isinstance(dissemination_datetime_to, datetime)
                else dissemination_datetime_to
            )
        if release_datetime_from:
            params["release_datetime_from"] = (
                release_datetime_from.isoformat()
                if isinstance(release_datetime_from, datetime)
                else release_datetime_from
            )
        if release_datetime_to:
            params["release_datetime_to"] = (
                release_datetime_to.isoformat()
                if isinstance(release_datetime_to, datetime)
                else release_datetime_to
            )
        if type:
            params["type"] = type
        if search:
            params["search"] = search
        if ordering:
            params["ordering"] = ordering

        response = await self._make_request("GET", "/filings/", params)
        return cast(FilingResponse, response)

    async def get_filing(self, filing_id: int) -> Filing:
        """
        Retrieve details for a specific filing.

        Args:
            filing_id: ID of the filing to retrieve

        Returns:
            Filing object
        """
        response = await self._make_request("GET", f"/filings/{filing_id}/")
        return cast(Filing, response)

    async def list_companies(
        self,
        page: int = 1,
        page_size: int = 50,
        countries: Optional[str] = None,
        sector: Optional[int] = None,
        industry_group: Optional[int] = None,
        industry: Optional[int] = None,
        sub_industry: Optional[int] = None,
    ) -> CompanyResponse:
        """
        List companies with optional filtering.

        Args:
            page: Page number for pagination
            page_size: Number of results per page
            countries: Filter by ISO 3166-1 alpha-2 country code
            sector: Filter by GICS sector code
            industry_group: Filter by GICS industry group code
            industry: Filter by GICS industry code
            sub_industry: Filter by GICS sub-industry code

        Returns:
            List of company objects
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}

        # Add optional filters
        if countries:
            params["countries"] = countries
        if sector:
            params["sector"] = sector
        if industry_group:
            params["industry_group"] = industry_group
        if industry:
            params["industry"] = industry
        if sub_industry:
            params["sub_industry"] = sub_industry

        response = await self._make_request("GET", "/companies/", params)
        return cast(CompanyResponse, response)

    async def get_company(self, company_id: int) -> Company:
        """
        Retrieve details for a specific company.

        Args:
            company_id: ID of the company to retrieve

        Returns:
            Company object
        """
        response = await self._make_request("GET", f"/companies/{company_id}/")
        return cast(Company, response)

    async def list_filing_types(self, page: int = 1, page_size: int = 50) -> FilingTypeResponse:
        """
        List all filing types.

        Args:
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            List of filing type objects
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        response = await self._make_request("GET", "/filing-types/", params)
        return cast(FilingTypeResponse, response)

    async def get_filing_type(self, type_id: str) -> dict[str, str]:
        """
        Retrieve details for a specific filing type.

        Args:
            type_id: ID of the filing type to retrieve

        Returns:
            Filing type object
        """
        response = await self._make_request("GET", f"/filing-types/{type_id}/")
        return cast(dict[str, str], response)

    async def list_sources(self, page: int = 1, page_size: int = 50) -> SourceResponse:
        """
        List all filing sources.

        Args:
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            List of source objects
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        response = await self._make_request("GET", "/filings/sources/", params)
        return cast(SourceResponse, response)

    async def get_source(self, source_id: str) -> dict[str, str]:
        """
        Retrieve details for a specific filing source.

        Args:
            source_id: ID of the source to retrieve

        Returns:
            Source object
        """
        response = await self._make_request("GET", f"/filings/sources/{source_id}/")
        return cast(dict[str, str], response)

    async def list_sectors(self, page: int = 1, page_size: int = 50) -> SectorResponse:
        """
        List all sectors.

        Args:
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            List of sector objects
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        response = await self._make_request("GET", "/sectors/", params)
        return cast(SectorResponse, response)

    async def get_sector(self, sector_id: int) -> dict[str, str]:
        """
        Retrieve details for a specific sector.

        Args:
            sector_id: ID of the sector to retrieve

        Returns:
            Sector object
        """
        response = await self._make_request("GET", f"/sectors/{sector_id}/")
        return cast(dict[str, str], response)

    async def list_industry_groups(self, page: int = 1, page_size: int = 50) -> IndustryResponse:
        """
        List all industry groups.

        Args:
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            List of industry group objects
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        response = await self._make_request("GET", "/industry-groups/", params)
        return cast(IndustryResponse, response)

    async def get_industry_group(self, group_id: int) -> dict[str, Any]:
        """
        Retrieve details for a specific industry group.

        Args:
            group_id: ID of the industry group to retrieve

        Returns:
            Industry group object
        """
        response = await self._make_request("GET", f"/industry-groups/{group_id}/")
        return cast(dict[str, Any], response)

    async def list_industries(self, page: int = 1, page_size: int = 50) -> IndustryResponse:
        """
        List all industries.

        Args:
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            List of industry objects
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        response = await self._make_request("GET", "/industries/", params)
        return cast(IndustryResponse, response)

    async def get_industry(self, industry_id: int) -> dict[str, Any]:
        """
        Retrieve details for a specific industry.

        Args:
            industry_id: ID of the industry to retrieve

        Returns:
            Industry object
        """
        response = await self._make_request("GET", f"/industries/{industry_id}/")
        return cast(dict[str, Any], response)

    async def list_sub_industries(self, page: int = 1, page_size: int = 50) -> IndustryResponse:
        """
        List all sub-industries.

        Args:
            page: Page number for pagination
            page_size: Number of results per page

        Returns:
            List of sub-industry objects
        """
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        response = await self._make_request("GET", "/sub-industries/", params)
        return cast(IndustryResponse, response)

    async def get_sub_industry(self, sub_industry_id: int) -> dict[str, Any]:
        """
        Retrieve details for a specific sub-industry.

        Args:
            sub_industry_id: ID of the sub-industry to retrieve

        Returns:
            Sub-industry object
        """
        response = await self._make_request("GET", f"/sub-industries/{sub_industry_id}/")
        return cast(dict[str, Any], response)

    async def get_ticker_by_name(self, company_name: str) -> Optional[str]:
        """
        Get company ticker symbol by company name.

        Args:
            company_name: Name of the company to search for

        Returns:
            Company ticker symbol if found, None otherwise
        """
        logger.info(f"Starting search for company ticker: {company_name}")

        try:
            # Normalize the search name
            search_name = company_name.lower().strip()

            # Try exact name first
            params = {"page": 1, "page_size": 10, "search": company_name, "ordering": "name"}
            response = await self._make_request("GET", "/companies/", params)
            logger.debug(f"API Response: {response}")

            if not isinstance(response.get("results"), list):
                logger.error(f"Invalid response format: {response}")
                return None

            results = response["results"]
            count = response.get("count", 0)
            logger.info(f"Found {count} potential matches")

            # Check for exact or close matches
            for company in results:
                logger.debug(f"Checking company: {company}")
                if not isinstance(company, dict):
                    logger.warning(f"Company data is not a dict: {type(company)}")
                    continue
                if "name" not in company or "ticker" not in company:
                    logger.warning(f"Company missing required fields: {company.keys()}")
                    continue

                company_name_lower = company["name"].lower().strip()
                # Check for exact match
                if company_name_lower == search_name:
                    logger.info(f"Found exact match: {company['name']}")
                    ticker = company.get("ticker")
                    if ticker:
                        logger.info(f"Found ticker: {ticker}")
                        return ticker
                    else:
                        logger.warning(f"Company {company['name']} has no ticker")
                        return None
                # Check if search term is contained in company name
                elif search_name in company_name_lower or company_name_lower in search_name:
                    logger.info(f"Found fuzzy match: {company['name']}")
                    ticker = company.get("ticker")
                    if ticker:
                        logger.info(f"Found ticker: {ticker}")
                        return ticker
                    else:
                        logger.warning(f"Company {company['name']} has no ticker")
                        continue

            # If no matches found, try with partial name
            if "." in search_name or " " in search_name:
                partial_name = search_name.split(".")[0].split(" ")[0]  # Take first word before dot or space
                if partial_name != search_name:
                    logger.info(f"Trying partial name search with: {partial_name}")
                    params["search"] = partial_name
                    response = await self._make_request("GET", "/companies/", params)
                    logger.debug(f"Partial search response: {response}")

                    if not isinstance(response.get("results"), list):
                        logger.error(f"Invalid response format in partial search: {response}")
                        return None

                    for company in response["results"]:
                        logger.debug(f"Checking partial match company: {company}")
                        if not isinstance(company, dict):
                            logger.warning(f"Company data in partial search is not a dict: {type(company)}")
                            continue
                        if "name" not in company or "ticker" not in company:
                            logger.warning(f"Company in partial search missing required fields: {company.keys()}")
                            continue

                        company_name_lower = company["name"].lower().strip()
                        if search_name in company_name_lower or company_name_lower in search_name:
                            logger.info(f"Found match with partial name: {company['name']}")
                            ticker = company.get("ticker")
                            if ticker:
                                logger.info(f"Found ticker: {ticker}")
                                return ticker
                            else:
                                logger.warning(f"Company {company['name']} has no ticker")
                                continue

            logger.info(f"No matches found for '{company_name}'")
            return None

        except Exception as e:
            logger.error(f"Error searching for company: {str(e)}")
            return None

    async def get_primary_isin_by_name(self, company_name: str) -> Optional[str]:
        """
        Get company ISIN by company name.

        Args:
            company_name: Name of the company to search for

        Returns:
            Company ISIN if found, None otherwise
        """
        logger.info(f"Starting search for company: {company_name}")

        try:
            # Normalize the search name
            search_name = company_name.lower().strip()

            # Try exact name first
            params = {"page": 1, "page_size": 10, "search": company_name, "ordering": "name"}
            response = await self._make_request("GET", "/companies/", params)
            logger.debug(f"API Response: {response}")  # Log full response for debugging

            if not isinstance(response.get("results"), list):
                logger.error(f"Invalid response format: {response}")
                return None

            results = response["results"]
            count = response.get("count", 0)
            logger.info(f"Found {count} potential matches")

            # Check for exact or close matches
            for company in results:
                logger.debug(f"Checking company: {company}")  # Log each company for debugging
                if not isinstance(company, dict):
                    logger.warning(f"Company data is not a dict: {type(company)}")
                    continue
                if "name" not in company:
                    logger.warning(f"Company missing 'name' field: {company.keys()}")
                    continue

                company_name_lower = company["name"].lower().strip()
                # Check for exact match
                if company_name_lower == search_name:
                    logger.info(f"Found exact match: {company['name']}")
                    # Get ISINs from company data
                    isins = company.get("isins", [])
                    if isins:
                        logger.info(f"Found ISINs: {isins}")
                        return isins[0]  # Return first ISIN
                    else:
                        logger.warning(f"Company {company['name']} has no ISINs")
                        return None
                # Check if search term is contained in company name
                elif search_name in company_name_lower or company_name_lower in search_name:
                    logger.info(f"Found fuzzy match: {company['name']}")
                    # Get ISINs from company data
                    isins = company.get("isins", [])
                    if isins:
                        logger.info(f"Found ISINs: {isins}")
                        return isins[0]  # Return first ISIN
                    else:
                        logger.warning(f"Company {company['name']} has no ISINs")
                        continue  # Try next company if this one has no ISINs

            # If no matches found, try with partial name
            if "." in search_name or " " in search_name:
                partial_name = search_name.split(".")[0].split(" ")[0]  # Take first word before dot or space
                if partial_name != search_name:
                    logger.info(f"Trying partial name search with: {partial_name}")
                    params["search"] = partial_name
                    response = await self._make_request("GET", "/companies/", params)
                    logger.debug(f"Partial search response: {response}")  # Log partial search response

                    if not isinstance(response.get("results"), list):
                        logger.error(f"Invalid response format in partial search: {response}")
                        return None

                    for company in response["results"]:
                        logger.debug(f"Checking partial match company: {company}")
                        if not isinstance(company, dict):
                            logger.warning(f"Company data in partial search is not a dict: {type(company)}")
                            continue
                        if "name" not in company:
                            logger.warning(f"Company in partial search missing 'name' field: {company.keys()}")
                            continue

                        company_name_lower = company["name"].lower().strip()
                        if search_name in company_name_lower or company_name_lower in search_name:
                            logger.info(f"Found match with partial name: {company['name']}")
                            # Get ISINs from company data
                            isins = company.get("isins", [])
                            if isins:
                                logger.info(f"Found ISINs: {isins}")
                                return isins[0]  # Return first ISIN
                            else:
                                logger.warning(f"Company {company['name']} has no ISINs")
                                continue  # Try next company if this one has no ISINs

            logger.info(f"No matches found for '{company_name}'")
            return None

        except Exception as e:
            logger.error(f"Error searching for company: {str(e)}")
            return None
