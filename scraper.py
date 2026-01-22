import asyncio
from crawl4ai import AsyncWebCrawler
import os

OUTPUT_DIR = "raw text"

async def extract_text(source_name, url):

    # makes the output file path
    output_file = f"{source_name.replace(' ', '_')}_raw_text.txt"

    # create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, output_file), 'w', encoding='utf-8') as f:
        f.write(f"Source: {source_name}\nURL: {url}\n\n")

        async with AsyncWebCrawler() as crawler:
            # Run the crawler on a URL
            result = await crawler.arun(url)

            # Print the extracted content
            print(result.markdown)
            f.write(result.markdown)