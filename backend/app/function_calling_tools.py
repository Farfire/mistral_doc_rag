# https://docs.mistral.ai/capabilities/function_calling/

from mistralai import Mistral
import os
import functools
import pandas as pd
import json
import requests
from app.embed import _get_chunk_embedding, load_index
from app.utils import load_json
import numpy as np


# Assuming we have the following data
data = {
    "transaction_id": ["T1001", "T1002", "T1003", "T1004", "T1005"],
    "customer_id": ["C001", "C002", "C003", "C002", "C001"],
    "payment_amount": [125.50, 89.99, 120.00, 54.30, 210.20],
    "payment_date": [
        "2021-10-05",
        "2021-10-06",
        "2021-10-07",
        "2021-10-05",
        "2021-10-08",
    ],
    "payment_status": ["Paid", "Unpaid", "Paid", "Paid", "Pending"],
}

# Create DataFrame
df = pd.DataFrame(data)
google_api_key = os.getenv("GOOGLE_API_KEY")


texts = load_json("docs_all_site_contents")
index, text_embeddings, chunks = load_index()


def get_official_documentation_on_question(question: str) -> list[str]:
    num_chunks = 4
    question_embeddings = np.array([_get_chunk_embedding(question)])
    D, I = index.search(question_embeddings, k=num_chunks)  # distance, index
    retrieved_chunks = []

    print("TITLES:")
    for i in I.tolist()[0]:
        title = chunks[i]
        print(title)
        for text in texts:
            if text["title"] == title:
                retrieved_chunks.append(text["content"])

    return retrieved_chunks


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_official_documentation_on_question",
            "description": "Get the official documentation from Mistral AI DOCUMENTATION on a given question. The given question must be translated to English. Not all information is useful!",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to find relevant documentation information for. The question must be asked in English.",
                    },
                },
                "required": ["question"],
            },
        },
    }
]


names_to_functions = {
    "get_official_documentation_on_question": get_official_documentation_on_question
}
