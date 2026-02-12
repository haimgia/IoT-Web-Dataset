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

    with open(text_file, "w", encoding="utf-8") as f:
        for i, paragraph in enumerate(paragraphs):
            print(f"Paragraph {i+1}:")
            print(paragraph)
            print("-" * 20)

            f.write(f"{paragraph}\n\n")


    


if __name__ == "__main__":
    generate_triples_from_pdf(os.path.join(PDF_FOLDER, "Accuracy of Fitbit Devices Systematic Review and Narrative Syntheses of Quantitative Data.pdf"))