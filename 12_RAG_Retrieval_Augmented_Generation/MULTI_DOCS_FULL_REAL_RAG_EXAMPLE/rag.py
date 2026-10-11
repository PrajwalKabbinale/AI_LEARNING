from openai import OpenAI
from dotenv import load_dotenv
import os
import numpy as np
from pathlib import Path

load_dotenv(override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")

# Embedding model ≠ chat model

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = os.getenv("MODEL_NAME")
client = OpenAI()

def cosine_similarity(vector1, vector2):
    v1 = np.array(vector1)
    v2 = np.array(vector2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def load_documents():
    documents = {}
    folder = Path("knowledge")
    for file in folder.glob("*.txt"):
        documents[file.name] = file.read_text(
            encoding="utf-8"
        )
    return documents

def create_embedding(content):
    embedding1 = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=content,
    ).data[0].embedding
    return embedding1

documents = load_documents()

document_embeddings = {}

for filename, content in documents.items():
    document_embeddings[filename] = create_embedding(content)

print("=" * 40)
print("      My AI Assistant")
print("=" * 40)

while True:
    user_input = input("\nYou : ")
    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    question_embedding = create_embedding(user_input)
    best_score = -1
    best_document = None

    for filename, embedding in document_embeddings.items():
        score = cosine_similarity(question_embedding, embedding)
        print(f"Score for {filename}: {score}")
        if score > best_score:
            best_score = score
            best_document = filename
    
    print(f"Best document: {best_document}")

    RAG_DOC_CONTENT = documents[best_document]
    print(f"\nRAG_DOC_CONTENT: {RAG_DOC_CONTENT}")

    prompt = f"Use ONLY the Context below to answer.\nIf the user typed a topic or keyword (not a full question), briefly explain what it is using the Context.\nIf the Context truly has nothing relevant, say 'I don't know.'\n\nRAG_Context: {RAG_DOC_CONTENT}\n\nUSER_INPUT: {user_input}"

    print(f"\n\nAI_ASSISTANT_PROMPT: {prompt}")

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    print("\nAI :", response.choices[0].message.content)

