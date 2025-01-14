import os
import pytest
from financial_reports import FinancialReportsClient

@pytest.mark.asyncio
async def test_list_filings():
    client = FinancialReportsClient(verify_ssl=False)
    try:
        filings = await client.list_filings(company_isin="FR0000073298")
        assert isinstance(filings, dict)
        assert "count" in filings
        assert "results" in filings
        assert isinstance(filings["results"], list)
    finally:
        await client.close()

@pytest.mark.asyncio
async def test_list_companies():
    client = FinancialReportsClient(verify_ssl=False)
    try:
        companies = await client.list_companies(countries="de")
        assert isinstance(companies, dict)
        assert "count" in companies
        assert "results" in companies
        assert isinstance(companies["results"], list)
    finally:
        await client.close()

@pytest.mark.asyncio
async def test_get_isin_by_name():
    client = FinancialReportsClient(verify_ssl=False)
    try:
        isin = await client.get_primary_isin_by_name("SAP")
        assert isinstance(isin, str) or isin is None
    finally:
        await client.close()

@pytest.mark.asyncio
async def test_invalid_api_key():
    client = FinancialReportsClient(api_key="invalid-key", verify_ssl=False)
    with pytest.raises(ValueError, match="Invalid API key|Insufficient permissions"):
        await client.list_filings()
