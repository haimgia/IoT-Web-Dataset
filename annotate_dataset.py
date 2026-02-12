import pandas as pd
import ast
from tqdm import tqdm
from dotenv import load_dotenv
import os
from openai import OpenAI
import pymupdf
import re
import asyncio
from crawl4ai import AsyncWebCrawler

load_dotenv()

RAW_TEXT_FOLDER = "raw text"
GEN_TRIPLES_FOLDER = "generated_triples"

PDF_FOLDER = "scholarly_papers"
PRIVACY_POLICY_FOLDER = "privacy_policies"

PRIVACY_POLICY_SOURCES = {"Google Privacy Policy": "https://policies.google.com/privacy?hl=en",
           "Microsoft Privacy Policy": "https://www.microsoft.com/en-us/privacy",
           "SmartThings Privacy Policy": "https://eula.samsungiotcloud.com/legal/us/en/pps.html",
           "Amazon Alexa and Echo Privacy Policy": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GVP69FUJ48X9DK8V",
           "Cisco Privacy Policy": "https://store.google.com/magazine/google_pixel_watch_compare?hl=en-US&pli=1",
           "Apple Privacy Policy": "https://www.apple.com/legal/privacy/en-ww/",
           "Huawei Privacy Policy": "https://consumer.huawei.com/en/privacy/privacy-statement-huawei/",
           "Samsung Privacy Policy": "https://www.samsung.com/us/account/privacy-policy/",
           "Ring Privacy Policy": "https://ring.com/privacy-notice?srsltid=AfmBOoo0ZH4T_iO5KXl9j1oenf05o819_C_nf95hTSg4BXXSmBgkJOyB",
           "Schneider Electric": "https://www.se.com/us/en/about-us/legal/data-privacy/"}

GPT_OSS_ENDPOINT = os.getenv("GPT_OSS_ENDPOINT")

def generate_triples_from_csv(csv_file):

    # reads csv file into a DataFrame
    df = pd.read_csv(csv_file)

    # processes each row to generate triples
    for index, row in tqdm(df.iterrows()):

        # reads the text file to extract data
        file = row['text file']
        print(f"Processing row {index}: {file}")
        with open(file, "r", encoding="utf-8") as f:
            data = f.read()

        # calls openAI endpoint
        client = OpenAI(
        base_url=GPT_OSS_ENDPOINT,
        api_key="dummy_key",
        )

        # First API call to extract triples
        response = client.chat.completions.create(
        model="gpt-oss:120b",
        messages=[
                {"role": "system", "content": "You are an expert at extracting subject-predicate-object triples from product descriptions."},
                {"role": "user", "content": f"Extract subject-predicate-object triples in the form of (subject, predicate, object) from the following product description:\n\n{data}\n\nFormat the output as a list of triples."}
                ]
        )

        # Extract the assistant message with reasoning_details
        response = response.choices[0].message

        print(response.content)

        # added LLM annotated triples to the DataFrame
        df.at[index, 'Triples'] = response.content

    # saves the updated DataFrame to a new CSV file
    output_csv_file = "annotated_" + os.path.basename(csv_file)
    df.to_csv(output_csv_file, index=False)
    print(f"Annotated CSV file saved as: {output_csv_file}")

def generate_triples_from_pdf(pdf_file):

    text = ""

    # reads the pdf file
    doc = pymupdf.open(pdf_file)


    for i, page in tqdm(enumerate(doc)): # iterate the document pages
        page_text = page.get_text().encode("utf8") # get plain text (is in UTF-8)

        #print(f"Extracted text from page {i + 1}:\n {text.decode('utf8')}\n")

        text += page_text.decode('utf8') + "\n"

    # This regex splits by one or more whitespace characters, including newlines, 
    # capturing common paragraph breaks while handling different formatting.
    paragraphs = re.split(r'\s{2,}', text) 

    # Filter out any empty strings that might result from the split
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    # Print or process the paragraphs

    text_file = f"raw text/{pdf_file.replace('.pdf', '.txt').replace(' ', '_')}"
    triples_output = f"generated_triples/{pdf_file.replace('.pdf', '.txt').replace(' ', '_')}"


    with open(text_file, "w", encoding="utf-8") as f:
        with open(triples_output, "w", encoding="utf-8") as g:
            for i, paragraph in tqdm(enumerate(paragraphs)):

                # writes the paragraph splits into the raw text file
                f.write(f"{paragraph}\n\n")

                triples = generate_triples(paragraph)

                # writes the paragraphs and its associated triples to the triples file
                g.write(f"Text: {paragraph}\nTriples: {triples}\n\n\n")


def generate_triples(text):

    # calls openAI endpoint
    client = OpenAI(
    base_url=GPT_OSS_ENDPOINT,
    api_key="dummy_key",
    )

    # First API call to extract triples
    response = client.chat.completions.create(
    model="gpt-oss:120b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are an expert in extracting structured IoT knowledge graph triples. "
                "Extract only meaningful IoT-related subject-predicate-object triples "
                "from technical text."
            )
        },
        {
            "role": "user",
            "content": f"""
                Extract IoT-related subject-predicate-object triples from the text below.

                Extraction Rules:
                - Only extract triples relevant to IoT systems, including but not limited to:
                devices, sensors, platforms, protocols, connectivity,
                data types, cloud services, edge components,
                security features, monitoring capabilities,
                automation, integration, and analytics.
                - Ignore purely marketing language (e.g., "innovative", "best-in-class").
                - Use concise, canonical entity names.
                - Normalize predicates to short, machine-friendly verbs
                (e.g., supports, monitors, integrates_with, uses_protocol, provides, detects).
                - Split compound actions into separate atomic triples.
                - Avoid duplicate triples.
                - Output ONLY a Python list of triples.
                - Format strictly as:
                [
                    ("subject", "predicate", "object"),
                    ...
                ]

                Text:
                {text}
                """
        }
    ]
    )

    # Extract the assistant message with reasoning_details
    response = response.choices[0].message

    triples = response.content

    return triples
    #print(response.content)

async def generate_triples_from_privacy_policies(source_name, url):
     # makes the output file path
    output_file = f"{source_name.replace(' ', '_')}.txt"

    # create output directory if it doesn't exist
    os.makedirs(os.path.join(RAW_TEXT_FOLDER, PRIVACY_POLICY_FOLDER), exist_ok=True)
    os.makedirs(os.path.join(GEN_TRIPLES_FOLDER, PRIVACY_POLICY_FOLDER), exist_ok=True)

    with open(os.path.join(RAW_TEXT_FOLDER, PRIVACY_POLICY_FOLDER, output_file), 'w', encoding='utf-8') as f:
        f.write(f"Source: {source_name}\nURL: {url}\n\n")

        async with AsyncWebCrawler() as crawler:
            # Run the crawler on a URL
            result = await crawler.arun(url)

            # Strip markdown hyperlinks
            text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", result.markdown)

            # Remove Markdown images: ![alt](url)
            text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)

            # Remove other hyperlinks
            text = re.sub(r"\[[^\]]*\]\([^)]+\)", "", text)

            # Remove empty/noisy lines
            text = "\n".join(
                line for line in text.splitlines()
                if len(line.strip()) > 20
            )

            # Remove raw URLs
            #text = re.sub(r"http[s]?://\S+", "", text)

            sections = extract_sections(text)

            for title, content in sections:
                print("TITLE:", title)
                print("CONTENT:", content)

                f.write(f"{title}\n{content}\n\n")



def extract_sections(markdown_text):
    pattern = r"(#{1,3})\s+(.*)"

    sections = []
    current_title = "INTRO"
    current_content = []

    for line in markdown_text.splitlines():
        match = re.match(pattern, line)

        if match:
            # Save previous section
            if current_content:
                sections.append((current_title, "\n".join(current_content).strip()))

            # Start new section
            current_title = match.group(2)
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_content:
        sections.append((current_title, "\n".join(current_content).strip()))

    return sections
    


    


if __name__ == "__main__":
    # for pdf_file in tqdm(os.listdir(PDF_FOLDER)):
    #     generate_triples_from_pdf(os.path.join(PDF_FOLDER, pdf_file))

    # testing scraping with privacy policies
    for source_name, url in PRIVACY_POLICY_SOURCES.items():
        asyncio.run(generate_triples_from_privacy_policies(source_name, url))
        
