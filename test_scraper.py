# test_scrapers.py
import asyncio
from deep_research_py.data_acquisition.scraper import PlaywrightScraper, RequestsScraper

async def compare_scrapers():
    # Test URL
    url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC7192202/"
    
    # Initialize both scrapers
    playwright_scraper = PlaywrightScraper()
    requests_scraper = RequestsScraper()
    
    try:
        # Setup both scrapers
        await playwright_scraper.setup()
        await requests_scraper.setup()
        
        # Scrape with both
        print("🔍 Testing Playwright scraper...")
        playwright_result = await playwright_scraper.scrape(url)
        
        print("🔍 Testing Requests scraper...")
        requests_result = await requests_scraper.scrape(url)
        
        # Compare results
        print(f"\n📊 Comparison Results:")
        print(f"Playwright text length: {len(playwright_result.text):,} characters")
        print(f"Requests text length: {len(requests_result.text):,} characters")
        print(f"Status codes: Playwright={playwright_result.status_code}, Requests={requests_result.status_code}")
        
        # Show previews
        print(f"\n🎭 Playwright preview (first 500 chars):")
        print(playwright_result.text[:500])
        print(f"\n🌐 Requests preview (first 500 chars):")
        print(requests_result.text[:500])
        
        # Check similarity
        similarity = len(set(playwright_result.text.split()) & set(requests_result.text.split()))
        print(f"\n📈 Word overlap: {similarity} common words")
        
    finally:
        # Cleanup
        await playwright_scraper.teardown()
        await requests_scraper.teardown()

if __name__ == "__main__":
    asyncio.run(compare_scrapers())