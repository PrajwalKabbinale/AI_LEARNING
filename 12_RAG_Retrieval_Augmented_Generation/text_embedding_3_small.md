# `text-embedding-3-small` — OpenAI embeddings for RAG

Hands-on companion after [`3_lm_types_and_embeddings.md`](./3_lm_types_and_embeddings.md). Folder `12_RAG_Retrieval_Augmented_Generation`.

**Practice:** [`embedding_demo.py`](./embedding_demo.py) · walkthrough [`embedding_demo.md`](./embedding_demo.md)

**Next:** [`cosine_similarity.md`](./cosine_similarity.md) (compare two vectors) · [`6_vector_store.md`](./6_vector_store.md) (where vectors live) · LangChain practice in [`13_LANGCHAIN/`](../13_LANGCHAIN/) (`OpenAIEmbeddings` + Chroma)

Related: [`keyword_rag_gradio_chat.md`](./keyword_rag_gradio_chat.md) (keyword match — no embeddings yet)

---

## Index

| # | Topic |
|---|--------|
| 1 | [What is an embedding?](#1-what-is-an-embedding) |
| 2 | [What is `text-embedding-3-small`?](#2-what-is-text-embedding-3-small) |
| 3 | [Embeddings vs chat models](#3-embeddings-vs-chat-models) |
| 4 | [Create your first embedding](#4-create-your-first-embedding) |
| 5 | [Compare two embeddings](#5-compare-two-embeddings) |
| 6 | [Tiny semantic search (idea)](#6-tiny-semantic-search-idea) |
| 7 | [How this fits into RAG](#7-how-this-fits-into-rag) |
| 8 | [Why not use GPT-4.1-nano for embeddings?](#8-why-not-use-gpt-41-nano-for-embeddings) |
| 9 | [Check your understanding](#9-check-your-understanding) |

---

## 1. What is an embedding?

Three sentences:

- "I love dogs."
- "I enjoy playing with puppies."
- "The stock market fell today."

A computer does not naturally know that the first two are related. An **embedding model** turns each sentence into a **vector** (list of numbers) that captures aspects of meaning.

```text
"I love dogs."
        ↓
 text-embedding-3-small
        ↓
[0.021, -0.014, 0.083, ...]   ← 1,536 floats by default
```

Numbers above are illustrative. Real output differs each run shape (length stays 1536 by default).

**Key idea:** text in → numerical meaning out → compare vectors to find similar text even when wording differs.

---

## 2. What is `text-embedding-3-small`?

OpenAI model whose job is to **convert text into embeddings**. It does not write chat answers.

| Spec | Value |
|------|--------|
| Model name | `text-embedding-3-small` |
| Default dimensions | **1,536** |
| Max input per text | 8,192 tokens |
| Price (approx.) | $0.02 / 1M tokens |

Specs/pricing can change — check [OpenAI embeddings docs](https://platform.openai.com/docs/guides/embeddings).

---

## 3. Embeddings vs chat models

| Chat model | Embedding model |
|------------|-----------------|
| Generates answers | Generates vectors |
| Reasoning / conversation | Semantic search / retrieval |
| Output is usually text | Output is a list of numbers |
| Example: `gpt-4.1-nano` | Example: `text-embedding-3-small` |

In RAG you typically use **both**: embedding model finds relevant chunks; chat model answers using those chunks.

---

## 4. Create your first embedding

```bash
pip install openai python-dotenv
```

Needs `OPENAI_API_KEY` in `.env` (same as your other OpenAI scripts).

Run:

```bash
python3 embedding_demo.py
```

Line-by-line: [`embedding_demo.md`](./embedding_demo.md).

Core API call:

```python
from openai import OpenAI

client = OpenAI()
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Kubernetes automatically restarts failed containers.",
)
embedding = response.data[0].embedding
print(len(embedding))       # 1536
print(embedding[:5])        # first five floats
```

| Piece | Role |
|-------|------|
| `client.embeddings.create(...)` | Call OpenAI embeddings API |
| `model=...` | Which embedding model |
| `input=...` | Text (or list of texts) to embed |
| `response.data[0].embedding` | The vector |

You can pass **many strings** in one `input=` list when indexing a corpus.

---

## 5. Compare two embeddings

Document:

> "Kubernetes restarts containers when they fail."

Question:

> "What happens when a pod's application crashes?"

Wording differs; meaning is related. Embed both, then compare vectors.

Common measure: **cosine similarity** — full note: [`cosine_similarity.md`](./cosine_similarity.md). OpenAI embedding vectors are **normalized** by default, so the **dot product** ranks the same way as cosine similarity for those vectors.

```text
Document  →  Vector A
Query     →  Vector B
Similarity(A, B)  →  higher ≈ more related
```

Scores are **not** a probability that the answer is correct — only a ranking signal.

---

## 6. Tiny semantic search (idea)

Foundation of RAG retrieval: embed docs → embed question → rank by similarity.

1. Embed several short documents (one API call can take a **list** of strings).  
2. Embed the user question with the **same** model.  
3. Score each document (e.g. **dot product** — same ranking as cosine for normalized OpenAI vectors).  
4. Keep the top matches as context for the chat model.

This folder’s practice script stops at step “embed one string” — see [`embedding_demo.py`](./embedding_demo.py). Full retrieve-from-store practice is in [`13_LANGCHAIN/`](../13_LANGCHAIN/).

---

## 7. How this fits into RAG

```text
1. Knowledge base (PDF, Markdown, code, docs)
2. Chunk documents
3. Embed chunks with text-embedding-3-small
4. Store vectors in a vector DB (Chroma, FAISS, …)
        ↓ user asks a question
5. Embed query (same model) → retrieve nearest chunks
6. Send chunks + question to a chat model → grounded answer
```

**Rule:** same embedding model (and dimensionality) for index and query. Change the model → **re-embed and rebuild** the index.

This folder’s keyword script skips steps 3–5 and matches dict keys by word. LangChain notebooks in **13** do the full embed → Chroma path.

---

## 8. Why not use GPT-4.1-nano for embeddings?

| Feature | `gpt-4.1-nano` | `text-embedding-3-small` |
|---------|----------------|--------------------------|
| Primary job | Generate text | Produce vectors |
| Typical output | Text / structured replies | 1,536-dim vector |
| Semantic search | Not via the chat API | Designed for this |
| Role in RAG | Final answer | Retrieve relevant docs |

You could ask a chat model to “output a list of numbers,” but those numbers are **not** trained/exposed as a proper embedding space for vector search.

**Use both:**

1. Embed docs + query with `text-embedding-3-small`.  
2. Retrieve relevant passages.  
3. Answer with `gpt-4.1-nano` (or whatever `MODEL_NAME` you use).

---

## 9. Check your understanding

**Q:** In a RAG app, what is the primary job of `text-embedding-3-small`?

- A. Generate the final natural-language answer  
- B. Convert text into vectors that help find related content  
- C. Store documents permanently in a vector database  
- D. Train a new GPT model on your documents  

<details>
<summary>Answer</summary>

**B.** The embedding model turns text into vectors for retrieval. Storage is the vector DB; the final answer is the chat model.

</details>

**Next step:** run [`embedding_demo.py`](./embedding_demo.py), read [`embedding_demo.md`](./embedding_demo.md), then [`cosine_similarity.md`](./cosine_similarity.md), then [`6_vector_store.md`](./6_vector_store.md).
