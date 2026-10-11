# First OpenAI embedding with text-embedding-3-small.
# Needs OPENAI_API_KEY in .env (same as other scripts in this folder).

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("OPENAI_API_KEY not set — add it to .env")

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Kubernetes automatically restarts failed containers.",
)

embedding = response.data[0].embedding
print("Number of dimensions:", len(embedding))
print("First 5 values:", embedding[:5])
