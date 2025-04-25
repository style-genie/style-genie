import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig, LLMContentFilter,DefaultMarkdownGenerator
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def main():
    # 1) Browser config: headless, bigger viewport, no proxy
    browser_conf = BrowserConfig(
        headless=True,
        viewport_width=1280,
        viewport_height=720
    )

    # 2) Example extraction strategy
    schema = {
        "name": "Products",
        "baseSelector": "li[data-test='product-tile']",
        "fields": [
            {"name": "title", "selector": ".productName", "type": "text"},
            {"name": "brand", "selector": ".productBrandName", "type": "text"},
            {"name": "price", "selector": "span[data-test^='productCurrentPrice']", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
            {"name": "img_src", "selector": "img.product-listing-dpr", "type": "attribute", "attribute": "srcset"}
        ]
    }
    extraction = JsonCssExtractionStrategy(schema)

    # 3) Example LLM content filtering

    gemini_config = LLMConfig(
        provider="gemini/gemini-2.0-flash-001",
        api_token = "AIzaSyC2pgSkdovwkpQgBLuWTpb-JMruxXXJIeM"
    )

    # Initialize LLM filter with specific instruction
    filter = LLMContentFilter(
        llm_config=gemini_config,  # or your preferred provider
        instruction="""
        Extract information about the fashion shopping items.
        Include:
        - item name
        - item brand
        - item price
        - item links
        - item image links
        Example:
            {
            "name": "Navy Single-Breasted Flannel Taormina-Fit Blazer"
            "brand": "DOLCE&GABBANA"
            "price": "\u20ac1268"
            "link": "https://www.ssense.com/en-de/men/product/dolce-and-gabbana/navy-single-breasted-flannel-taormina-fit-blazer/15860681"
            "image": "https://img.ssensemedia.com/images/f_auto,c_limit,h_2800,w_1725/242003M195000_1/dolceandgabbana-navy-single-breasted-flannel-taormina-fit-blazer.jpg"
            }
        Format the output as json output.
        """,
        chunk_token_threshold=500,  # Adjust based on your needs
        verbose=True
    )

    md_generator = DefaultMarkdownGenerator(
    content_filter=filter,
    options={"ignore_links": True}
    )
    run_conf = CrawlerRunConfig(
        markdown_generator=md_generator,
        extraction_strategy=extraction,
        cache_mode=CacheMode.BYPASS
    )


    async with AsyncWebCrawler(config=browser_conf) as crawler:
        # 4) Execute the crawl
        result = await crawler.arun(url="https://www.ssense.com/en-de/women", config=run_conf)

        if result.success:
            print("Extracted content:", result)
            print("Extracted content:", result.extracted_content)
        else:
            print("Error:", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())
