import pandas as pd
import ast
from tqdm import tqdm
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

GPT_OSS_ENDPOINT = os.getenv("GPT_OSS_ENDPOINT")

def generate_triples(csv_file):

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
        model="gpt-oss:latest",
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