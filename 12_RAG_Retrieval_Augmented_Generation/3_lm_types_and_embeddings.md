# LM types and embeddings (for RAG)

Chapter notes (folder `12_RAG_Retrieval_Augmented_Generation`).

**Read order:** `3` of `8` — after [`2_rag_architecture_and_workflow.md`](./2_rag_architecture_and_workflow.md) §8 (autoencoder vs autoregressive vs encoder–decoder) for the full architecture picture; this note focuses on RAG roles and embeddings. **Hands-on next:** [`text_embedding_3_small.md`](./text_embedding_3_small.md). **Then:** [`6_vector_store.md`](./6_vector_store.md).

Related: [`1_introduction_to_rag.md`](./1_introduction_to_rag.md) · [`what_is_huggingface.md`](../7_HUGGING_FACE/what_is_huggingface.md) (pipelines / encoder models)

---

## Index

| # | Topic |
|---|--------|
| 1 | [Autoregressive language models](#1-autoregressive-language-models) |
| 2 | [Autoencoding language models](#2-autoencoding-language-models) |
| 3 | [Which type for which RAG role?](#3-which-type-for-which-rag-role) |
| 4 | [Vector embeddings](#4-vector-embeddings) |
| 5 | [Embedding model examples](#5-embedding-model-examples) |

---

## 1. Autoregressive language models

Given **past tokens**, predict the **next** token — then repeat (next token given full history so far).

This is the dominant **chat / completion** paradigm.

| Examples | Role in RAG |
|----------|-------------|
| GPT-4, Claude, Gemini, Llama (instruct) | **Generator** — writes the final answer after context is in the prompt |

**Layman:** reads left-to-right and “continues the story” — your RAG **answer** usually comes from this family.

---

## 2. Autoencoding language models

Take a **full input** (past + present context in one pass) and produce **outputs that summarize or classify** the whole input — not token-by-token open-ended generation in the GPT style.

Typical tasks:

- **Sentiment** — positive vs negative  
- **Classification** — label buckets  
- **Similarity / encoding** — fixed-size representation of meaning  

You may have seen these via **Hugging Face `pipeline`** tasks (e.g. sentiment, fill-mask) — encoder-style models.

---

## 3. Which type for which RAG role?

| RAG stage | Common model type | Job |
|-----------|-------------------|-----|
| **Embeddings / retrieval** | Autoencoding-style **encoder** | Turn chunk and query into vectors for search |
| **Final answer** | **Autoregressive** FM | Generate natural language from augmented prompt |

Same product stack often uses **two different models**: small/fast **embedding** model + large **chat** model.

---

## 4. Vector embeddings

An **embedding** maps text (or other input) to a **list of numbers** — a **vector** — that captures **semantic meaning**.

- Think of 3 numbers as \((x, y, z)\) in space.  
- Real systems use **hundreds or thousands** of dimensions — same idea, impossible to draw, but **distance** between vectors ≈ **similarity of meaning**.

Similar sentences → vectors **close** together → good for “find chunks like this question.”

That is why RAG retrieval is also called **semantic search**.

---

## 5. Embedding model examples

| Family | Notes |
|--------|--------|
| **BERT** (Google) | Classic encoder; foundation for many embedding approaches |
| **OpenAI embeddings** (e.g. `text-embedding-3-small`) | API-based vectors; common in tutorials and production |
| Open-source encoders on Hugging Face | Self-hosted, language-specific options |

Pick one embedding model for **both** indexing and query embedding; mixing unrelated models breaks similarity search.

**Practice:** call OpenAI `text-embedding-3-small` — [`text_embedding_3_small.md`](./text_embedding_3_small.md) · [`embedding_demo.py`](./embedding_demo.py) · [`embedding_demo.md`](./embedding_demo.md).

For ingest + query flow, see [`2_rag_architecture_and_workflow.md`](./2_rag_architecture_and_workflow.md).
