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

        
        file = row['text file']
        print(f"Processing row {index}: {file}")
        with open(file, "r", encoding="utf-8") as f:
            data = f.read()

        continue
        # Implement triple extraction logic here
        # For now, just printing the data
        print(f"Processing row {index}: {file}")


        client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="dummy_key",
        )

        # First API call to extract triples
        response = client.chat.completions.create(
        model="openai/gpt-oss-120b:free",
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

    # saves the updated DataFrame back to the CSV file  
    df_annotated = df.iloc[:ROWS]
    df_annotated.to_csv(annotated_file, index=False)