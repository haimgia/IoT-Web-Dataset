import pandas as pd
import ast
from tqdm import tqdm
from dotenv import load_dotenv
import os
from openai import OpenAI
import pymupdf
import re

load_dotenv()

PDF_FOLDER = "scholarly_papers"

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

                # print(f"Paragraph {i+1}:")
                # print(paragraph)
                # print("-" * 20)

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


    


if __name__ == "__main__":
    for pdf_file in tqdm(os.listdir(PDF_FOLDER)):
        generate_triples_from_pdf(os.path.join(PDF_FOLDER, pdf_file))
