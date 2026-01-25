import asyncio
from crawl4ai import AsyncWebCrawler
import os
import pymupdf
from tqdm import tqdm

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

def extract_text_from_pdf(pdf_file):
    doc = pymupdf.open(pdf_file) # open a document

    # makes the output file path
    output_file = pdf_file.replace('.pdf', '.txt')

    # create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open (os.path.join(OUTPUT_DIR, os.path.basename(output_file)), 'w', encoding='utf-8') as f:
        for i, page in tqdm(enumerate(doc)): # iterate the document pages
            text = page.get_text().encode("utf8") # get plain text (is in UTF-8)

            print(f"Extracted text from page {i + 1}:\n {text.decode('utf8')}\n")
            f.write(text.decode('utf8'))