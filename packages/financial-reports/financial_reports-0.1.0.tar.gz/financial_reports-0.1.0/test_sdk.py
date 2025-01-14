import asyncio
import os
from financial_reports import FinancialReportsClient

async def test_all_endpoints():
    api_key = os.getenv("FINANCIAL_REPORTS_API_KEY")
    if not api_key:
        print("Please set FINANCIAL_REPORTS_API_KEY environment variable")
        return
    
    # Print masked API key for verification
    masked_key = f"{api_key[:4]}...{api_key[-4:]}"
    print(f"Using API key: {masked_key}")
        
    client = FinancialReportsClient(api_key=api_key, verify_ssl=False)
    try:
        # Test filings
        print("\nTesting filings endpoint...")
        filings = await client.list_filings(company_isin="FR0000073298")
        print(f"Found {filings['count']} filings")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
