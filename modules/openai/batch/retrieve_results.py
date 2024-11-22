from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def retrieve_results(output_file_id, output_path):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_ORG_ID")
    )

    file_response = client.files.content(output_file_id)

    with open(output_path, "wb") as out_file:
        out_file.write(file_response)

    print(f"Batch results downloaded to {output_path}")

if __name__ == "__main__":
    output_file_id = "your_output_file_id_here" # output file id here obtained from check_batch_status.py
    retrieve_results(output_file_id, "batch_output.jsonl")
