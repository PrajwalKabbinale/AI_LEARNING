from dotenv import load_dotenv
from openai import OpenAI
import os
import numpy as np

def cosine_similarity(vector1, vector2):
    v1 = np.array(vector1)
    v2 = np.array(vector2)

    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


load_dotenv(override=True)
openai_api_key = os.getenv("OPENAI_API_KEY")

MODEL_NAME = "text-embedding-3-small"
client = OpenAI()

text1 = "Python is a programming language."
text2 = "Python is used for software development."
text3 = "Pizza is a delicious food."

embedding1 = client.embeddings.create(
    model=MODEL_NAME,
    input=text1
).data[0].embedding

embedding2 = client.embeddings.create(
    model=MODEL_NAME,
    input=text2
).data[0].embedding

embedding3 = client.embeddings.create(
    model=MODEL_NAME,
    input=text3
).data[0].embedding

print("embedding1")
print(len(embedding1))
print("embedding2")
print(len(embedding2))
print("embedding3")
print(len(embedding3))

score1 = cosine_similarity(
    embedding1,
    embedding2
)
score2 = cosine_similarity(
    embedding1,
    embedding3
)
score3 = cosine_similarity(
    embedding2,
    embedding3
)

score4 = cosine_similarity(
    embedding1,
    embedding1
)

print("score1")
print(score1)
print("score2")
print(score2)
print("score3")
print(score3)
print("score4")
print(score4)