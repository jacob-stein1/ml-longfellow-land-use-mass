from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def check_batch_status(batch_id):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        organization=os.getenv("OPENAI_ORG_ID")
    )

    batch_status = client.batches.retrieve(batch_id)
    print(f"Batch Status: {batch_status.status}")
    return batch_status

if __name__ == "__main__":
    batch_id = "" # batch id here obtained from create_batch.py
    check_batch_status(batch_id)
